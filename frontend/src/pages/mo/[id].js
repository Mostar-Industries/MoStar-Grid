import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function MoScript() {
  const router = useRouter();
  const { id } = router.query;
  const [script, setScript] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    const fetchScript = async () => {
      try {
        const response = await fetch(/api/mo-scripts/);
        const data = await response.json();
        setScript(data);
        setLoading(false);
      } catch (error) {
        console.error(Failed to fetch MoScript :, error);
        setLoading(false);
      }
    };

    fetchScript();
  }, [id]);

  if (!id) return <p>Loading...</p>;

  return (
    <div className="container">
      <Head>
        <title>MoScript {id}</title>
      </Head>

      <h1>MoScript {id}</h1>

      {loading ? (
        <p>Loading script data...</p>
      ) : script ? (
        <div className="script-container">
          <h2>{script.name}</h2>
          <pre>{script.content}</pre>
        </div>
      ) : (
        <p>Script not found</p>
      )}
    </div>
  );
}
