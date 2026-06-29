'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/agents');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen text-gray-600">
      Redirection vers le guichet d&apos;enrôlement…
    </div>
  );
}
