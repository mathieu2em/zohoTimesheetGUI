/* global console, process */
/* eslint-disable no-console, no-process-exit */
const { exec } = require('child_process');
const http = require('http');
const https = require('https');
const open = require('open');
const { openStdin, stdin } = require('process');
const { URL } = require('url');

const HOST = process.env.ZOHO_REDIRECT_HOST || 'localhost'
const PORT = process.env.ZOHO_REDIRECT_PORT || '8888'
const CLIENT_ID = "***REMOVED***"
const CLIENT_SECRET = "***REMOVED***"
const REDIRECT_URI = process.env.ZOHO_REDIRECT_URI || `http://${HOST}:${PORT}/zoho/callback`
const SCOPE = process.env.ZOHO_SCOPE || 'ZohoBooks.fullaccess.all'
const ZOHO_BASE = 'https://accounts.zoho.com/oauth/v2'

const authUrl = (scope, clientId, redirectUri) => {
  return `${ZOHO_BASE}/auth?scope=${scope}&client_id=${clientId}&response_type=code&access_type=offline&redirect_uri=${redirectUri}`
}

const tokenUrl = (code, clientId, clientSecret, redirectUri) => {
  return `${ZOHO_BASE}/token?code=${code}&redirect_uri=${redirectUri}&client_id=${clientId}&client_secret=${clientSecret}&grant_type=authorization_code`
}

const tradeCodeForToken = (code) => {
  const url = new URL(tokenUrl(code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI))
  const options = {
    hostname: url.hostname,
    port: url.port,
    path: `${url.pathname}${url.search}`,
    method: 'POST',
  }

  const req = https.request(options, (res) => {
    if (res.statusCode === 200) {
      res.setEncoding('utf8')
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        try {
          const tokenData = JSON.parse(data)
          //const jsonString = JSON.stringify(tokenData, null, '  ')
          process.stdout.write(tokenData['access_token'])
          //process.stdin.write(jsonString)

        } catch (err) {
          console.log(err)
        }
        shutdown()
      })
    } else {
      console.log(`Failed to trade code for tokens: ${res.statusCode} ${res.message}`)
      shutdown()
    }
  })
  req.end()
}

const server = http.createServer((req, res) => {
  const { url } = req
  if (!url.includes('zoho')) {
    res.end()
    return
  }

  const queryString = url.includes('?') ? url.split('?')[1] : ''
  const params = {}
  if (queryString.includes('=')) {
    queryString.split('&')
      .map(part => part.split('='))
      .reduce((acc, part) => {
        const [ key, val ] = part
        acc[key] = val
        return acc
      }, params)
  }
  res.end('<HTML><HEAD><TITLE>Zoho OAuth2 Tool</TITLE></HEAD><BODY> we have now acquired our token ! :D </BODY></HTML>', 'utf-8')

  if (params.code) {
    tradeCodeForToken(params.code)
  }
})

const shutdown = () => {
  server.close()
  process.exit(0)
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
// console.log(`listening on ${HOST}:${PORT}`)
server.listen({ port: PORT, host: HOST })

const url = `${authUrl(SCOPE, CLIENT_ID, REDIRECT_URI)}`

exec(`open '${url}'`, (err, stdout, stderr) => {
  if (err) {
    if (err.message.includes('Command failed')) {
      //console.log(`Please copy/paste this into your browser of choice:\n\t${url}`)
      open(url)
    }
  }
})
