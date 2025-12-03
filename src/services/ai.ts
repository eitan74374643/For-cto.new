import axios from 'axios';

// Replace with real keys or use a backend proxy
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY';

export const transcribeAudio = async (uri: string): Promise<string> => {
  console.log('Transcribing:', uri);
  
  // MOCK IMPLEMENTATION
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("Hey, I was just thinking about the project meeting tomorrow. We really need to focus on the UI/UX design before we move to the backend implementation. Also, don't forget to buy milk on your way home. Let's sync up at 10 AM.");
    }, 2000);
  });

  /* REAL IMPLEMENTATION (OpenAI Whisper)
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'audio.m4a',
    type: 'audio/m4a',
  } as any);
  formData.append('model', 'whisper-1');

  const response = await axios.post('https://api.openai.com/v1/audio/transcriptions', formData, {
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data.text;
  */
};

export const summarizeText = async (text: string): Promise<string> => {
  console.log('Summarizing:', text);

  // MOCK IMPLEMENTATION
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("• Focus on UI/UX before backend.\n• Reminder: Buy milk.\n• Sync meeting at 10 AM.");
    }, 1500);
  });

  /* REAL IMPLEMENTATION (OpenAI GPT)
  const response = await axios.post('https://api.openai.com/v1/chat/completions', {
    model: "gpt-3.5-turbo",
    messages: [
      { role: "system", content: "Summarize the following text into 1-3 clear bullet points." },
      { role: "user", content: text }
    ]
  }, {
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
  });
  return response.data.choices[0].message.content;
  */
};
