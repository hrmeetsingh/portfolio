import { Fragment, useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import { skeleton } from '../../utils';
import { SanitizedBooks } from '../../interfaces/sanitized-config';
import { FaBook } from 'react-icons/fa';

interface Book {
  title: string;
  author: string;
  coverUrl?: string;
  link?: string;
  status: 'reading' | 'read';
}

interface BooksCardProps {
  loading: boolean;
  books: SanitizedBooks;
}

const BooksCard: React.FC<BooksCardProps> = ({ loading, books }) => {
  const [booksList, setBooksList] = useState<Book[]>([]);
  const [booksLoading, setBooksLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBooks = useCallback(async () => {
    if (!books.display || !books.userId) {
      return;
    }

    try {
      setBooksLoading(true);
      setError(null);

      const allBooks: Book[] = [];
      let feedFailed = false;

      const parseWidget = (
        widgetJs: string,
        status: 'reading' | 'read',
      ): Book[] => {
        const literal = widgetJs.match(
          /var widget_code = '([\s\S]*?)'\s*\n\s*var widget_div/,
        );
        if (!literal) {
          throw new Error('Unexpected Goodreads widget response');
        }

        const html = literal[1].replace(
          /\\(u[0-9a-fA-F]{4}|.)/g,
          (_, c: string) => {
            if (c.length === 5)
              return String.fromCharCode(parseInt(c.slice(1), 16));
            return c === 'n' ? '\n' : c === 't' ? '\t' : c === 'r' ? '\r' : c;
          },
        );
        const safeUrl = (raw: string | null | undefined): string => {
          try {
            const url = new URL(raw || '', 'https://www.goodreads.com');
            return url.protocol === 'https:' || url.protocol === 'http:'
              ? url.href
              : '';
          } catch {
            return '';
          }
        };
        const doc = new DOMParser().parseFromString(html, 'text/html');

        return Array.from(
          doc.querySelectorAll('[class^="gr_custom_each_container_"]'),
        ).map((item) => {
          const titleLink = item.querySelector<HTMLAnchorElement>(
            '[class^="gr_custom_title_"] a',
          );
          return {
            title: titleLink?.textContent?.trim() || 'Unknown Title',
            author:
              item
                .querySelector('[class^="gr_custom_author_"] a')
                ?.textContent?.trim() || 'Unknown Author',
            coverUrl: safeUrl(item.querySelector('img')?.getAttribute('src')),
            link: safeUrl(titleLink?.getAttribute('href')),
            status,
          };
        });
      };

      try {
        const { data } = await axios.get<string>(books.proxyUrl, {
          params: { shelf: 'read' },
          responseType: 'text',
        });
        allBooks.push(...parseWidget(data, 'read'));
      } catch (err) {
        console.warn('Failed to load read books:', err);
        feedFailed = true;
      }

      setBooksList(allBooks);

      if (allBooks.length === 0) {
        setError(
          feedFailed
            ? 'Goodreads feed unavailable (private shelves or changed widget)'
            : 'No books found in your Goodreads shelves',
        );
      }
    } catch (err) {
      console.error('Error fetching books:', err);
      setError('Failed to load books from Goodreads');
    } finally {
      setBooksLoading(false);
    }
  }, [books.display, books.userId, books.proxyUrl]);

  useEffect(() => {
    if (books.display) {
      fetchBooks();
    }
  }, [books.display, fetchBooks]);

  const renderSkeleton = () => {
    const array = [];
    for (let index = 0; index < 3; index++) {
      array.push(
        <div key={index} className="flex gap-4 py-3">
          <div className="flex-shrink-0">
            {skeleton({
              widthCls: 'w-16',
              heightCls: 'h-24',
              shape: 'rounded',
            })}
          </div>
          <div className="flex-grow">
            {skeleton({
              widthCls: 'w-3/4',
              heightCls: 'h-4',
              className: 'mb-2',
            })}
            {skeleton({ widthCls: 'w-1/2', heightCls: 'h-3' })}
          </div>
        </div>,
      );
    }
    return array;
  };

  const BookItem: React.FC<{ book: Book }> = ({ book }) => (
    <div className="flex gap-4 py-3 border-b border-base-300 last:border-b-0">
      <div className="flex-shrink-0">
        {book.coverUrl ? (
          <img
            src={book.coverUrl}
            alt={book.title}
            className="w-16 h-24 object-cover rounded shadow-sm"
          />
        ) : (
          <div className="w-16 h-24 bg-base-300 rounded flex items-center justify-center">
            <FaBook className="text-2xl text-base-content opacity-30" />
          </div>
        )}
      </div>
      <div className="flex-grow min-w-0">
        <h6 className="font-semibold text-sm text-base-content line-clamp-2">
          {book.link ? (
            <a
              href={book.link}
              target="_blank"
              rel="noreferrer"
              className="hover:text-primary transition-colors"
            >
              {book.title}
            </a>
          ) : (
            book.title
          )}
        </h6>
        <p className="text-xs text-base-content text-opacity-60 mt-1">
          {book.author}
        </p>
        <span
          className={`inline-block mt-2 text-xs px-2 py-1 rounded-full ${
            book.status === 'reading'
              ? 'bg-primary bg-opacity-20 text-primary'
              : 'bg-base-300 text-base-content text-opacity-60'
          }`}
        >
          {book.status === 'reading' ? 'Currently Reading' : 'Read'}
        </span>
      </div>
    </div>
  );

  if (!books.display) {
    return null;
  }

  return (
    <div className="card shadow-lg compact bg-base-100">
      <div className="card-body">
        <div className="mx-3 mb-2">
          <h5 className="card-title">
            {loading ? (
              skeleton({ widthCls: 'w-32', heightCls: 'h-8' })
            ) : (
              <span className="text-base-content opacity-100 flex items-center gap-2">
                <FaBook className="text-lg" />
                {books.header || 'Books'}
              </span>
            )}
          </h5>
        </div>
        <div className="text-base-content text-opacity-100">
          {loading || booksLoading ? (
            renderSkeleton()
          ) : error ? (
            <div className="text-center py-4">
              <p className="text-sm text-error opacity-70">{error}</p>
              <p className="text-xs text-base-content text-opacity-50 mt-2">
                Check the Goodreads user ID and proxyUrl in the config file
              </p>
            </div>
          ) : booksList.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-sm text-base-content text-opacity-60">
                No books found
              </p>
            </div>
          ) : (
            <Fragment>
              {booksList.slice(0, books.limit || 5).map((book, index) => (
                <BookItem key={index} book={book} />
              ))}
            </Fragment>
          )}
        </div>
      </div>
    </div>
  );
};

export default BooksCard;
