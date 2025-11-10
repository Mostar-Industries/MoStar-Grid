import express from 'express'
import { queryNeo4j } from '../services/mostar.service'

export const router = express.Router()

router.post('/query', async (req, res) => {
  const { message } = req.body
  const result = await queryNeo4j(message)
  res.json(result)
})
