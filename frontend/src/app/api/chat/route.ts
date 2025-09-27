import { NextRequest, NextResponse } from 'next/server';

interface ChatRequest {
  user_hash: string;
  project_id: string;
  query: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json();

    // Validate required fields
    if (!body.user_hash || !body.project_id || !body.query) {
      return NextResponse.json(
        { error: 'Missing required fields: user_hash, project_id, or query' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

    console.log('Sending to backend:', {
      url: `${backendUrl}/chat`,
      body: { user_hash: body.user_hash, project_id: body.project_id, query: body.query }
    });

    const response = await fetch(`${backendUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_hash: body.user_hash,
        project_id: body.project_id,
        query: body.query,
      }),
    });

    console.log('Backend response status:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend response data:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('Chat API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}