export default function handler(req, res) {
  const { id } = req.query;

  const fakeScripts = {
    \"1\": { name: \"Genesis\", content: \"print('Hello from MoScript 1')\" },
    \"2\": { name: \"Expansion\", content: \"console.log('Expanding consciousness')\" },
  };

  const script = fakeScripts[id];

  if (script) {
    res.status(200).json(script);
  } else {
    res.status(404).json({ error: 'MoScript not found' });
  }
}
