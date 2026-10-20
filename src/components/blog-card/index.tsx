import { useEffect, useState } from 'react';
import LazyImage from '../lazy-image';
import { AiOutlineContainer } from 'react-icons/ai';
import { getDevPost, getMediumPost } from '@arifszn/blog-js';
import { SanitizedBlog } from '../../interfaces/sanitized-config';
import { ga, skeleton } from '../../utils';
import { Article } from '../../interfaces/article';
import { wpBlogs } from './fallback-list';

const MEDIUM_ATTEMPTS = 3;

// getMediumPost swallows errors (e.g. rss2json 500s) and returns [], so an
// empty result is treated as a failure and retried with backoff.
const fetchMediumWithRetry = async (user: string): Promise<Article[]> => {
  for (let attempt = 0; attempt < MEDIUM_ATTEMPTS; attempt++) {
    const res = await getMediumPost({ user });
    if (res && res.length) {
      return res;
    }
    if (attempt < MEDIUM_ATTEMPTS - 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
    }
  }
  return [];
};

const cacheKey = (user: string) => `blog-cache-${user}`;

const readCache = (user: string): Article[] => {
  try {
    const raw = localStorage.getItem(cacheKey(user));
    if (!raw) return [];
    const parsed: Article[] = JSON.parse(raw);
    return parsed.map((a) => ({ ...a, publishedAt: new Date(a.publishedAt) }));
  } catch {
    return [];
  }
};

const writeCache = (user: string, articles: Article[]) => {
  try {
    localStorage.setItem(cacheKey(user), JSON.stringify(articles));
  } catch {
    // storage unavailable; ignore
  }
};

const BlogCard = ({
  loading,
  blog,
  googleAnalyticsId,
}: {
  loading: boolean;
  blog: SanitizedBlog;
  googleAnalyticsId?: string;
}) => {
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    let ignore = false;
    const update = (res: Article[]) => {
      if (!ignore) setArticles(res);
    };

    if (blog.source === 'medium') {
      fetchMediumWithRetry(blog.username).then((res) => {
        if (res.length) {
          writeCache(blog.username, res);
          update(res);
        } else {
          const cached = readCache(blog.username);
          update(cached.length ? cached : wpBlogs);
        }
      });
    } else if (blog.source === 'dev') {
      getDevPost({
        user: blog.username,
      }).then(update);
    } else {
      setArticles(wpBlogs);
    }

    return () => {
      ignore = true;
    };
  }, [blog.source, blog.username]);

  const renderSkeleton = () => {
    const array = [];
    for (let index = 0; index < blog.limit; index++) {
      array.push(
        <div className="card shadow-lg compact bg-base-100" key={index}>
          <div className="p-8 h-full w-full">
            <div className="flex items-center flex-col md:flex-row">
              <div className="avatar mb-5 md:mb-0">
                <div className="w-24 h-24 mask mask-square">
                  {skeleton({
                    widthCls: 'w-full',
                    heightCls: 'h-full',
                    shape: '',
                  })}
                </div>
              </div>
              <div className="w-full">
                <div className="flex items-start px-4">
                  <div className="w-full">
                    <h2>
                      {skeleton({
                        widthCls: 'w-full',
                        heightCls: 'h-8',
                        className: 'mb-2 mx-auto md:mx-0',
                      })}
                    </h2>
                    {skeleton({
                      widthCls: 'w-24',
                      heightCls: 'h-3',
                      className: 'mx-auto md:mx-0',
                    })}
                    <div className="mt-3">
                      {skeleton({
                        widthCls: 'w-full',
                        heightCls: 'h-4',
                        className: 'mx-auto md:mx-0',
                      })}
                    </div>
                    <div className="mt-4 flex items-center flex-wrap justify-center md:justify-start">
                      {skeleton({
                        widthCls: 'w-32',
                        heightCls: 'h-4',
                        className: 'md:mr-2 mx-auto md:mx-0',
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>,
      );
    }

    return array;
  };

  const renderArticles = () => {
    return articles && articles.length ? (
      articles.slice(0, blog.limit).map((article, index) => (
        <a
          className="card shadow-lg compact bg-base-100 cursor-pointer"
          key={index}
          href={article.link}
          onClick={(e) => {
            e.preventDefault();

            try {
              if (googleAnalyticsId) {
                ga.event('Click Blog Post', {
                  post: article.title,
                });
              }
            } catch (error) {
              console.error(error);
            }

            window?.open(article.link, '_blank');
          }}
        >
          <div className="p-4 h-full w-full">
            <div className="flex items-center flex-col md:flex-row">
              <div className="avatar mb-5 md:mb-0 opacity-90">
                <div className="w-24 h-24 mask mask-square border-l border-r border-t border-b">
                  <LazyImage
                    src={article.thumbnail}
                    alt={'thumbnail'}
                    placeholder={skeleton({
                      widthCls: 'w-full',
                      heightCls: 'h-full',
                      shape: '',
                    })}
                  />
                </div>
              </div>
              <div className="w-full">
                <div className="flex items-start px-4">
                  <div className="text-center md:text-left w-full">
                    <h2 className="font-medium text-base-content opacity-100">
                      {article.title}
                    </h2>
                    <p className="mt-3 text-base-content text-opacity-60 text-sm">
                      {article.description}
                    </p>
                    <div className="mt-4 flex items-center flex-wrap justify-center md:justify-start">
                      {article.categories.map((category, index2) => (
                        <div
                          className="py-2 px-2 text-xs leading-3 rounded-full bg-base-300 mr-1 mb-1 opacity-50 text-base-content"
                          key={index2}
                        >
                          #{category}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </a>
      ))
    ) : (
      <div className="text-center mb-6">
        <AiOutlineContainer className="mx-auto h-12 w-12 opacity-30" />
        <p className="mt-1 text-sm opacity-50 text-base-content">
          No recent post
        </p>
      </div>
    );
  };

  return (
    <div className="col-span-1 lg:col-span-2">
      <div className="grid grid-cols-2 gap-6">
        <div className="col-span-2">
          <div
            className={`card compact bg-base-100 ${
              loading || (articles && articles.length)
                ? 'shadow bg-opacity-40'
                : 'shadow-lg'
            }`}
          >
            <div className="card-body">
              <div className="mx-3 mb-2">
                <h5 className="card-title">
                  {loading ? (
                    skeleton({ widthCls: 'w-28', heightCls: 'h-8' })
                  ) : (
                    <span className="text-base-content opacity-100">Blogs</span>
                  )}
                </h5>
              </div>
              <div className="col-span-2">
                <div className="grid grid-cols-1 gap-4">
                  {loading || !articles ? renderSkeleton() : renderArticles()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogCard;
