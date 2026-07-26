package polls

import "database/sql"

// View 单个投票的实时视图（对齐 polls_api 的 _poll_view）。
type View struct {
	Type   string         `json:"type"`
	Counts map[string]int `json:"counts"`
	Total  int            `json:"total"`
	AvgPct *int           `json:"avgPct"`
	Mine   *string        `json:"mine"`
}

func countsQ(q queryer, code, occ string) (map[string]int, error) {
	rows, err := q.Query(
		"SELECT answer_key, COUNT(*) c FROM poll_votes WHERE poll_code=? AND occ_key=? AND answer_key IS NOT NULL GROUP BY answer_key",
		code, occ)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := map[string]int{}
	for rows.Next() {
		var k string
		var c int
		if err := rows.Scan(&k, &c); err != nil {
			return nil, err
		}
		out[k] = c
	}
	return out, rows.Err()
}

type queryer interface {
	Query(string, ...any) (*sql.Rows, error)
	QueryRow(string, ...any) *sql.Row
}

// PollViewOf 组装某投票视图。
func PollViewOf(q queryer, code, occ, token string) (View, error) {
	counts, err := countsQ(q, code, occ)
	if err != nil {
		return View{}, err
	}
	var mine *string
	if token != "" {
		var mk sql.NullString
		err := q.QueryRow("SELECT answer_key FROM poll_votes WHERE poll_code=? AND occ_key=? AND client_token=?",
			code, occ, token).Scan(&mk)
		if err == nil && mk.Valid {
			v := mk.String
			mine = &v
		}
	}
	total := 0
	for _, c := range counts {
		total += c
	}
	return View{Type: ByCode[code].Type, Counts: counts, Total: total, AvgPct: AvgFromCounts(ByCode[code], counts), Mine: mine}, nil
}

// AllViews 取某职业所有投票的视图。
func AllViews(db *sql.DB, occ, token string) (map[string]View, error) {
	out := map[string]View{}
	for _, p := range Polls {
		v, err := PollViewOf(db, p.Code, occ, token)
		if err != nil {
			return nil, err
		}
		out[p.Code] = v
	}
	return out, nil
}

// Vote 记一票（upsert 一人一票）并重算聚合，返回该投票视图。事务保证原子。
func Vote(db *sql.DB, code, occ, token, answer, ipHash string) (View, error) {
	tx, err := db.Begin()
	if err != nil {
		return View{}, err
	}
	if _, err := tx.Exec(
		"INSERT INTO poll_votes (poll_code, occ_key, client_token, answer_key, ip_hash) VALUES (?,?,?,?,?) "+
			"ON DUPLICATE KEY UPDATE answer_key=VALUES(answer_key), ip_hash=VALUES(ip_hash)",
		code, occ, token, answer, ipHash); err != nil {
		tx.Rollback()
		return View{}, err
	}
	if _, err := tx.Exec("DELETE FROM poll_agg WHERE poll_code=? AND occ_key=?", code, occ); err != nil {
		tx.Rollback()
		return View{}, err
	}
	if _, err := tx.Exec(
		"INSERT INTO poll_agg (poll_code, occ_key, answer_key, cnt) "+
			"SELECT poll_code, occ_key, answer_key, COUNT(*) FROM poll_votes "+
			"WHERE poll_code=? AND occ_key=? AND answer_key IS NOT NULL GROUP BY poll_code, occ_key, answer_key",
		code, occ); err != nil {
		tx.Rollback()
		return View{}, err
	}
	view, err := PollViewOf(tx, code, occ, token)
	if err != nil {
		tx.Rollback()
		return View{}, err
	}
	if err := tx.Commit(); err != nil {
		return View{}, err
	}
	return view, nil
}
