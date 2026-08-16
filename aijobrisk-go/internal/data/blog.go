package data

import (
	"os"
	"path/filepath"
	"sort"
)

// —— Blog / News ——
// 由 scripts/build_blog.py 从 content/blog/*.md 烘焙：
//   data/blog/index.json  元数据数组（本文件启动载入内存）
//   data/blog/{slug}.html 预渲染正文（启动一并读入 Post.Body）
// 英文 only。best-effort：缺文件则 blog 板块不显示，不影响主站。

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

var (
	blogPosts   []*BlogPost
	blogBySlug  map[string]*BlogPost
	blogByTag   map[string][]*BlogPost
	blogAuthors map[string]BlogAuthor
	// P1 反向内链索引：职业/行业/国家 -> 命中该键的文章（newest-first）。
	blogBySlugRel    map[string][]*BlogPost
	blogBySectorRel  map[string][]*BlogPost
	blogByCountryRel map[string][]*BlogPost
)

// loadBlog best-effort 载入 blog（缺文件静默跳过）。
func loadBlog() {
	blogPosts = nil
	blogBySlug = map[string]*BlogPost{}
	blogByTag = map[string][]*BlogPost{}
	blogAuthors = map[string]BlogAuthor{}
	blogBySlugRel = map[string][]*BlogPost{}
	blogBySectorRel = map[string][]*BlogPost{}
	blogByCountryRel = map[string][]*BlogPost{}

	var doc struct {
		Posts   []*BlogPost           `json:"posts"`
		Authors map[string]BlogAuthor `json:"authors"`
	}
	if err := readJSON(filepath.Join("blog", "index.json"), &doc); err != nil {
		return
	}
	blogAuthors = doc.Authors

	for _, p := range doc.Posts {
		// 正文（缺失则空，页面仍可渲染标题/元数据）。
		if b, err := os.ReadFile(filepath.Join(dataDir, "blog", p.Slug+".html")); err == nil {
			p.Body = string(b)
		}
		blogPosts = append(blogPosts, p)
		blogBySlug[p.Slug] = p
		for _, t := range p.Tags {
			blogByTag[t] = append(blogByTag[t], p)
		}
		for _, s := range p.RelatedSlugs {
			blogBySlugRel[s] = append(blogBySlugRel[s], p)
		}
		for _, s := range p.RelatedSectors {
			blogBySectorRel[s] = append(blogBySectorRel[s], p)
		}
		for _, cc := range p.RelatedCountries {
			blogByCountryRel[cc] = append(blogByCountryRel[cc], p)
		}
	}
	// 统一 newest-first（Python 已排，这里兜底保证）。
	sort.SliceStable(blogPosts, func(i, j int) bool { return blogPosts[i].PublishedAt > blogPosts[j].PublishedAt })
}

// BlogHas 是否有可用文章。
func BlogHas() bool { return len(blogPosts) > 0 }

// BlogPosts 全部文章（newest-first）。
func BlogPosts() []*BlogPost { return blogPosts }

// BlogBySlug 按 slug 取文章（无则 nil）。
func BlogBySlug(slug string) *BlogPost { return blogBySlug[slug] }

// BlogByTag 某标签下的文章（newest-first）。
func BlogByTag(tag string) []*BlogPost { return blogByTag[tag] }

// BlogAuthorByID 作者信息。
func BlogAuthorByID(id string) (BlogAuthor, bool) { a, ok := blogAuthors[id]; return a, ok }

// BlogTags 全部标签（按文章数降序、同数按字母序）。
func BlogTags() []string {
	tags := make([]string, 0, len(blogByTag))
	for t := range blogByTag {
		tags = append(tags, t)
	}
	sort.Slice(tags, func(i, j int) bool {
		if len(blogByTag[tags[i]]) != len(blogByTag[tags[j]]) {
			return len(blogByTag[tags[i]]) > len(blogByTag[tags[j]])
		}
		return tags[i] < tags[j]
	})
	return tags
}

// BlogForSlug / BlogForSector / BlogForCountry：P1 反向内链（职业/行业/国家页「相关资讯」）。
func BlogForSlug(slug string) []*BlogPost   { return blogBySlugRel[slug] }
func BlogForSector(id string) []*BlogPost   { return blogBySectorRel[id] }
func BlogForCountry(cc string) []*BlogPost  { return blogByCountryRel[cc] }
