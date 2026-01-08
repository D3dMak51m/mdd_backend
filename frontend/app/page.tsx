import { redirect } from 'next/navigation';

export default function Home() {
  // Next.js автоматически добавит basePath (/ops),
  // поэтому редирект на '/live' приведет пользователя на '/ops/live'
  redirect('/live');
}