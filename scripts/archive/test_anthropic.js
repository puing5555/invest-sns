import dotenv from 'dotenv'

// Load environment variables
dotenv.config({ path: '.env.local' })

const anthropicApiKey = process.env.ANTHROPIC_API_KEY

console.log('API Key exists:', !!anthropicApiKey)
console.log('API Key starts with:', anthropicApiKey?.substring(0, 10))

// Test with different Claude models
const models = [
  'claude-3-5-sonnet-20241022',
  'claude-3-5-sonnet-20240620', 
  'claude-3-sonnet-20240229',
  'claude-3-haiku-20240307',
  'claude-3-opus-20240229'
]

async function testModel(model) {
  try {
    console.log(`\n🧪 Testing model: ${model}`)
    
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': anthropicApiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: model,
        max_tokens: 50,
        messages: [
          {
            role: 'user',
            content: 'Hello, just testing the connection. Please respond briefly.'
          }
        ]
      })
    })

    if (response.ok) {
      const data = await response.json()
      console.log(`✅ ${model}: SUCCESS`)
      console.log(`Response: ${data.content[0].text.substring(0, 100)}...`)
      return model
    } else {
      const error = await response.text()
      console.log(`❌ ${model}: ${response.status} - ${error.substring(0, 200)}`)
    }
  } catch (error) {
    console.log(`❌ ${model}: ${error.message}`)
  }
  
  return null
}

async function main() {
  console.log('🔍 Testing Anthropic API connection...\n')
  
  for (const model of models) {
    const workingModel = await testModel(model)
    if (workingModel) {
      console.log(`\n🎯 Found working model: ${workingModel}`)
      break
    }
    
    // Wait a bit between tests
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
}

main().catch(console.error)