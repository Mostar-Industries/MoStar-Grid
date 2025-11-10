import express from 'express'
import dotenv from 'dotenv'
import cors from 'cors'
import { router as mostarRouter } from './routes/mostar.routes'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3000

app.use(cors())
app.use(express.json())
app.use('/mostar', mostarRouter)

app.listen(PORT, () => {
  console.log(`🔥 Mostar Grid backend running on http://localhost:${PORT}`)
})
