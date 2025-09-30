import { NextRequest, NextResponse } from 'next/server';

interface ProjectInfoParams {
  userHash: string;
  projectId: string;
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<ProjectInfoParams> }
) {
  try {
    const { userHash, projectId } = await params;

    // Validate required params
    if (!userHash || !projectId) {
      return NextResponse.json(
        { error: 'Missing userHash or projectId' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/projects/${userHash}/${projectId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Project info API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}