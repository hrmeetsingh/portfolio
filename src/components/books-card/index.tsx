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

      const parseRSSFeed = (
        xmlString: string,
        status: 'reading' | 'read',
      ): Book[] => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlString, 'text/xml');

        const parserError = xmlDoc.querySelector('parsererror');
        if (parserError) {
          throw new Error('Failed to parse RSS feed');
        }

        const items = xmlDoc.querySelectorAll('item');
        const parsedBooks: Book[] = [];

        items.forEach((item) => {
          const title =
            item.querySelector('title')?.textContent || 'Unknown Title';
          const author =
            item.querySelector('author_name')?.textContent || 'Unknown Author';
          const bookLink = item.querySelector('link')?.textContent || '';
          const bookId = item.querySelector('book_id')?.textContent || '';

          const description =
            item.querySelector('description')?.textContent || '';
          const imgMatch = description.match(/<img[^>]+src="([^">]+)"/);
          const coverUrl = imgMatch ? imgMatch[1] : '';

          parsedBooks.push({
            title,
            author,
            coverUrl,
            link: bookLink || `https://www.goodreads.com/book/show/${bookId}`,
            status,
          });
        });

        return parsedBooks;
      };

      const proxyUrl = 'https://corsproxy.io?url=';
      const currentlyReadingUrl = encodeURIComponent(
        `https://www.goodreads.com/review/list_rss/${books.userId}?shelf=currently-reading`,
      );
      const readUrl = encodeURIComponent(
        `https://www.goodreads.com/review/list_rss/${books.userId}?shelf=read`,
      );

      const [currentlyReadingResult, readResult] = await Promise.allSettled([
        axios.get(`${proxyUrl}${currentlyReadingUrl}`).then((res) => ({
          ...res,
          data: res.data.contents,
        })),
        axios.get(`${proxyUrl}${readUrl}`).then((res) => ({
          ...res,
          data: res.data.contents,
        })),
      ]);

      if (currentlyReadingResult.status === 'fulfilled') {
        try {
          const currentlyReadingBooks = parseRSSFeed(
            currentlyReadingResult.value.data,
            'reading',
          );
          allBooks.push(...currentlyReadingBooks);
        } catch (err) {
          console.warn('Failed to parse currently-reading books:', err);
        }
      }

      if (readResult.status === 'fulfilled') {
        try {
          const readBooks = parseRSSFeed(readResult.value.data, 'read');
          allBooks.push(...readBooks);
        } catch (err) {
          console.warn('Failed to parse read books:', err);
        }
      }

      allBooks.sort((a, b) => {
        if (a.status === 'reading' && b.status === 'read') return -1;
        if (a.status === 'read' && b.status === 'reading') return 1;
        return 0;
      });

      setBooksList(allBooks);

      if (allBooks.length === 0) {
        setError('No books found in your Goodreads shelves');
      }
    } catch (err) {
      console.error('Error fetching books:', err);
      setError('Failed to load books from Goodreads');
    } finally {
      setBooksLoading(false);
    }
  }, [books.display, books.userId]);

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
                Configure your Goodreads user ID in the config file
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
