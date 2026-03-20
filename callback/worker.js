import HTML from './index.html';

export default {
  async fetch(request) {
    return new Response(HTML, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8',
        'Cache-Control': 'no-store',
      },
    });
  },
};
