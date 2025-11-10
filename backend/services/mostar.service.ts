import { driver } from '../utils/graph'

export async function queryNeo4j(prompt: string) {
  const session = driver.session()
  try {
    const cypher = `MATCH (n) RETURN n LIMIT 5`
    const result = await session.run(cypher)
    return result.records.map(record => record.toObject())
  } finally {
    await session.close()
  }
}
