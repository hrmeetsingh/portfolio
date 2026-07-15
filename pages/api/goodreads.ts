import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { shelf, userId } = req.query;

  if (!shelf || !userId) {
    return res.status(400).json({ error: 'Missing required parameters' });
  }

  try {
    const response = await axios.get(
      `https://www.goodreads.com/review/list_rss/${userId}?shelf=${shelf}`,
      {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'application/xml'
        }
      }
    );

    res.setHeader('Content-Type', 'application/xml');
    res.status(200).send(response.data);
  } catch (error) {
    console.error('Error fetching Goodreads data:', error);
    res.status(500).json({ error: 'Failed to fetch Goodreads data' });
  }
}
