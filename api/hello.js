export default function handler(req, res) {
  res.status(200).json({ name: 'MoStar Grid API', status: 'online' });
}
