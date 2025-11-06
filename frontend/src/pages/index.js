import Link from 'next/link';
import Head from 'next/head';

export default function Home() {
  return (
    <div className="container">
      <Head>
        <title>MoStar Grid</title>
        <meta name="description" content="MoStar Grid Next.js Application" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>MoStar Grid</h1>
        <p>Welcome to the Next.js version</p>
        
        <div className="grid">
          <Link href="/dashboard">
            <div className="card">
              <h2>Dashboard &rarr;</h2>
              <p>View the MoStar Grid dashboard</p>
            </div>
          </Link>
          
          <Link href="/mo/1">
            <div className="card">
              <h2>MoScripts &rarr;</h2>
              <p>Explore MoScripts</p>
            </div>
          </Link>
        </div>
      </main>
    </div>
  );
}
