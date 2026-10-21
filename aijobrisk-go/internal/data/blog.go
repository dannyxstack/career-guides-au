package data

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

// —— Blog / News ——
// 由 scripts/build_blog.py 从 content/blog/*.md 烘焙：
//   data/blog/index.json  元数据数组（本文件启动载入内存）
//   data/blog/{slug}.html 预渲染正文（启动一并读入 Post.Body）
// 英文 only。best-effort：缺文件则 blog 板块不显示，不影响主站。
//
// 定时发布：index.json 里包含未来日期的文章，这里按「UTC 今天」在运行时过滤——
// 一次烘焙、一次部署，文章到日子自己出现，不需要每天重新烘焙或重启。
// 所有对外访问函数都只返回已到发布日的文章（未来文章的 slug 直接 404，不会泄露）。
//
// 热重载：ReloadBlog() 重读 data/blog/ 后原子替换，进程不重启、不停服。
// 读路径无锁（atomic.Pointer），重载与「跨日重建可见视图」才加锁。

// BlogAuthor 作者注册表项（authors.json）。
type BlogAuthor struct {
	Name   string   `json:"name"`
	Bio    string   `json:"bio"`
	URL    string   `json:"url"`
	SameAs []string `json:"same_as"`
}

// BlogPost 一篇文章的元数据 + 正文。
type BlogPost struct {
	Slug             string   `json:"slug"`
	Title            string   `json:"title"`
	Dek              string   `json:"dek"`
	Type             string   `json:"type"` // post | news
	PublishedAt      string   `json:"published_at"`
	UpdatedAt        string   `json:"updated_at"`
	Featured         bool     `json:"featured"`
	Author           string   `json:"author"`
	HeroImage        string   `json:"hero_image"`
	HeroAlt          string   `json:"hero_alt"`
	HeroCredit       string   `json:"hero_credit"`
	Tags             []string `json:"tags"`
	RelatedSlugs     []string `json:"related_slugs"`
	RelatedSectors   []string `json:"related_sectors"`
	RelatedCountries []string `json:"related_countries"`
	ReadingMin       int      `json:"reading_min"`
	WordCount        int      `json:"word_count"`
	TOC              string   `json:"toc"`
	SourceName       string   `json:"source_name"`
	SourceURL        string   `json:"source_url"`
	Body             string   `json:"-"` // 启动时从 {slug}.html 读入
}

// blogView 某一天可见的文章及其索引（全部 newest-first）。
type blogView struct {
	day          string
	posts        []*BlogPost
	bySlug       map[string]*BlogPost
	byTag        map[string][]*BlogPost
	bySlugRel    map[string][]*BlogPost // P1 反向内链：职业 -> 文章
	bySectorRel  map[string][]*BlogPost // 行业 -> 文章
	byCountryRel map[string][]*BlogPost // 国家 -> 文章
}

// blogStore 一次载入的全量快照（含尚未到期的定时文章）。
type blogStore struct {
	all     []*BlogPost // newest-first
	authors map[string]BlogAuthor
	mu      sync.Mutex // 只保护跨日重建 view
	view    atomic.Pointer[blogView]
}

var (
	blogCur   atomic.Pointer[blogStore]
	blogMu    sync.Mutex // 串行化 ReloadBlog，避免两次重载交错
	emptyView = &blogView{
		bySlug: map[string]*BlogPost{}, byTag: map[string][]*BlogPost{},
		bySlugRel: map[string][]*BlogPost{}, bySectorRel: map[string][]*BlogPost{},
		byCountryRel: map[string][]*BlogPost{},
	}
	// blogNow 当前时间；测试里替换以模拟跨日。
	blogNow = time.Now
)

// blogToday 发布日判定用 UTC 日期——与 GitHub Actions 的 cron 时区一致、与服务器时区无关。
func blogToday() string { return blogNow().UTC().Format("2006-01-02") }

// BlogDir 博客数据目录。线上设 AIJOBRISK_BLOG_DIR 指向独立的 git 镜像（ops/blog-pull.sh）：
// 不和代码目录共用——否则同步写进 data/blog 的文件（在仓库里是被跟踪的）会让线上
// git pull 因「本地改动会被覆盖」而拒绝。未设则用 data/blog。每次读取都重新取值，
// 所以只写在 .env 里（启动载入数据之后才读）也能在随后的 ReloadBlog 生效。
func BlogDir() string {
	if d := os.Getenv("AIJOBRISK_BLOG_DIR"); d != "" {
		return d
	}
	return filepath.Join(dataDir, "blog")
}

// readBlogStore 从博客目录读出一份全量快照。
func readBlogStore() (*blogStore, error) {
	var doc struct {
		Posts   []*BlogPost           `json:"posts"`
		Authors map[string]BlogAuthor `json:"authors"`
	}
	dir := BlogDir()
	b, err := os.ReadFile(filepath.Join(dir, "index.json"))
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(b, &doc); err != nil {
		return nil, fmt.Errorf("parse %s: %w", filepath.Join(dir, "index.json"), err)
	}
	s := &blogStore{authors: doc.Authors}
	if s.authors == nil {
		s.authors = map[string]BlogAuthor{}
	}
	for _, p := range doc.Posts {
		if p == nil || p.Slug == "" {
			continue
		}
		// 正文（缺失则空，页面仍可渲染标题/元数据）。
		if b, err := os.ReadFile(filepath.Join(dir, p.Slug+".html")); err == nil {
			p.Body = string(b)
		}
		s.all = append(s.all, p)
	}
	// 统一 newest-first（Python 已排，这里兜底保证）。
	sort.SliceStable(s.all, func(i, j int) bool { return s.all[i].PublishedAt > s.all[j].PublishedAt })
	return s, nil
}

// buildBlogView 从全量快照里挑出 day 当天及以前发布的文章并建索引。
func buildBlogView(all []*BlogPost, day string) *blogView {
	v := &blogView{
		day: day, bySlug: map[string]*BlogPost{}, byTag: map[string][]*BlogPost{},
		bySlugRel: map[string][]*BlogPost{}, bySectorRel: map[string][]*BlogPost{},
		byCountryRel: map[string][]*BlogPost{},
	}
	for _, p := range all {
		// YYYY-MM-DD 字符串可直接比较大小；空日期视为未排期，不展示。
		if p.PublishedAt == "" || p.PublishedAt > day {
			continue
		}
		v.posts = append(v.posts, p)
		v.bySlug[p.Slug] = p
		for _, t := range p.Tags {
			v.byTag[t] = append(v.byTag[t], p)
		}
		for _, s := range p.RelatedSlugs {
			v.bySlugRel[s] = append(v.bySlugRel[s], p)
		}
		for _, s := range p.RelatedSectors {
			v.bySectorRel[s] = append(v.bySectorRel[s], p)
		}
		for _, cc := range p.RelatedCountries {
			v.byCountryRel[cc] = append(v.byCountryRel[cc], p)
		}
	}
	return v
}

// curBlog 当天的可见视图；跨日时惰性重建一次（文章数量是几十级，重建微秒级）。
func curBlog() *blogView {
	s := blogCur.Load()
	if s == nil {
		return emptyView
	}
	day := blogToday()
	if v := s.view.Load(); v != nil && v.day == day {
		return v
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if v := s.view.Load(); v != nil && v.day == day {
		return v
	}
	v := buildBlogView(s.all, day)
	s.view.Store(v)
	return v
}

// loadBlog 启动时 best-effort 载入 blog（缺文件静默跳过，blog 板块不显示）。
func loadBlog() {
	s, err := readBlogStore()
	if err != nil {
		s = &blogStore{authors: map[string]BlogAuthor{}}
	}
	blogCur.Store(s)
}

// BlogStats 重载结果摘要。
type BlogStats struct {
	Total     int    `json:"total"`     // index.json 里的全部文章
	Visible   int    `json:"visible"`   // 今天已可见
	Scheduled int    `json:"scheduled"` // 尚未到发布日
	Next      string `json:"next"`      // 下一篇定时文章的发布日（无则空）
	Day       string `json:"day"`       // 判定所用的 UTC 日期
}

// ReloadBlog 重读 data/blog/ 并原子替换。读失败时保留旧数据并返回错误——
// 例如同步过程中 index.json 暂时缺失，不能因此把线上博客清空。
func ReloadBlog() (BlogStats, error) {
	blogMu.Lock()
	defer blogMu.Unlock()
	s, err := readBlogStore()
	if err != nil {
		return BlogStats{}, fmt.Errorf("reload blog: %w (kept previous %d posts)", err, len(BlogPosts()))
	}
	blogCur.Store(s)
	return BlogStatsNow(), nil
}

// BlogStatsNow 当前快照的统计（运维与重载接口用）。
func BlogStatsNow() BlogStats {
	st := BlogStats{Day: blogToday()}
	s := blogCur.Load()
	if s == nil {
		return st
	}
	st.Total = len(s.all)
	st.Visible = len(curBlog().posts)
	st.Scheduled = st.Total - st.Visible
	for _, p := range s.all { // newest-first，最后一个未来日期即「下一篇」
		if p.PublishedAt > st.Day {
			st.Next = p.PublishedAt
		}
	}
	return st
}

// BlogHas 是否有可用文章。
func BlogHas() bool { return len(curBlog().posts) > 0 }

// BlogPosts 已发布文章（newest-first）。
func BlogPosts() []*BlogPost { return curBlog().posts }

// BlogBySlug 按 slug 取已发布文章（无或尚未到发布日则 nil）。
func BlogBySlug(slug string) *BlogPost { return curBlog().bySlug[slug] }

// BlogByTag 某标签下的已发布文章（newest-first）。
func BlogByTag(tag string) []*BlogPost { return curBlog().byTag[tag] }

// BlogAuthorByID 作者信息。
func BlogAuthorByID(id string) (BlogAuthor, bool) {
	s := blogCur.Load()
	if s == nil {
		return BlogAuthor{}, false
	}
	a, ok := s.authors[id]
	return a, ok
}

// BlogTags 已发布文章的全部标签（按文章数降序、同数按字母序）。
func BlogTags() []string {
	byTag := curBlog().byTag
	tags := make([]string, 0, len(byTag))
	for t := range byTag {
		tags = append(tags, t)
	}
	sort.Slice(tags, func(i, j int) bool {
		if len(byTag[tags[i]]) != len(byTag[tags[j]]) {
			return len(byTag[tags[i]]) > len(byTag[tags[j]])
		}
		return tags[i] < tags[j]
	})
	return tags
}

// BlogForSlug / BlogForSector / BlogForCountry：P1 反向内链（职业/行业/国家页「相关资讯」）。
func BlogForSlug(slug string) []*BlogPost  { return curBlog().bySlugRel[slug] }
func BlogForSector(id string) []*BlogPost  { return curBlog().bySectorRel[id] }
func BlogForCountry(cc string) []*BlogPost { return curBlog().byCountryRel[cc] }
