# 🎤 Voice Recognition Feature

## Overview

The ERPNext AI Chat now includes **voice recognition** capabilities! Users can speak their queries instead of typing them.

## Features

### ✨ What's Included

- **🎤 Voice Input Button** - Click the microphone icon to start speaking
- **🔴 Live Recording Indicator** - Visual feedback when recording
- **📝 Real-time Transcription** - See your speech converted to text live
- **🤖 Auto-Submit** - Automatically sends query when you finish speaking
- **⌨️ Keyboard Shortcut** - Press `Ctrl+Shift+V` to start voice input
- **🚨 Error Handling** - Clear messages for permission issues
- **🌐 Browser Support** - Works in Chrome, Edge, and other Chromium browsers

## How to Use

### Method 1: Click the Microphone Button

1. Open AI Assistant chat
2. Click the **🎤** (microphone) button
3. Allow microphone access when prompted
4. Speak your query clearly
5. The query is automatically sent when you stop speaking

### Method 2: Keyboard Shortcut

1. Open AI Assistant chat
2. Press **Ctrl+Shift+V**
3. Speak your query
4. Done!

## Visual Feedback

### Recording States

**Before Recording:**
```
🎤 (Gray microphone icon)
```

**During Recording:**
```
🔴 (Red circle - pulsing animation)
Button background turns pink
Notification: "Listening... Speak now!"
```

**Transcribing:**
```
Text appears in input field as you speak
```

**Complete:**
```
Query automatically sent to AI
Response appears in chat
```

## Example Usage

### Voice Query Example

**You say:** "Show me pending sales orders"

**What happens:**
1. 🎤 Click microphone → 🔴 Recording starts
2. 📝 Text appears: "Show me pending sales orders"
3. 🚀 Query automatically sent
4. 🤖 AI responds with sales order list

### More Examples

```
Voice: "Search for customer ABC Corp"
→ AI finds and displays customer details

Voice: "Check stock balance for item laptop"
→ AI shows inventory levels

Voice: "What are today's pending orders?"
→ AI lists all pending orders
```

## Browser Compatibility

### ✅ Fully Supported
- **Google Chrome** (Desktop & Mobile)
- **Microsoft Edge**
- **Opera**
- **Brave**

### ⚠️ Partial Support
- **Safari** (macOS/iOS) - May require additional permissions

### ❌ Not Supported
- **Firefox** - Web Speech API not enabled by default
- **Internet Explorer** - Not supported

## Technical Details

### Speech Recognition API

Uses the **Web Speech API** (specifically `SpeechRecognition`):
- Real-time speech-to-text
- Interim results (live transcription)
- Automatic language detection
- Continuous recognition mode

### How It Works

```
User clicks mic
    ↓
Browser requests microphone permission
    ↓
Recording starts (visual feedback)
    ↓
Speech captured by browser
    ↓
Web Speech API converts to text
    ↓
Text appears in input field (live)
    ↓
When complete, auto-submit to AI
    ↓
AI processes and responds
```

### Code Flow

```javascript
// Initialize on page load
initVoiceRecognition()
    ↓
// User clicks microphone
toggleVoiceInput()
    ↓
// Browser listens
recognition.start()
    ↓
// Converts speech
recognition.onresult()
    ↓
// Auto-sends message
sendMessage()
```

## Configuration

### Language Settings

Default: **English (US)**

To change language, edit in `erpnext_ai_chat.js`:
```javascript
erpnext_ai_chat.recognition.lang = 'en-US';  // English (US)
// Other options:
// 'en-GB' - English (UK)
// 'es-ES' - Spanish
// 'fr-FR' - French
// 'de-DE' - German
// 'hi-IN' - Hindi
// 'zh-CN' - Chinese
```

### Recognition Settings

```javascript
erpnext_ai_chat.recognition.continuous = false;    // One-shot recording
erpnext_ai_chat.recognition.interimResults = true; // Show live transcription
erpnext_ai_chat.recognition.maxAlternatives = 1;   // Best match only
```

## Troubleshooting

### Issue: "Microphone access denied"

**Solution:**
1. Click the 🔒 (lock icon) in browser address bar
2. Change Microphone permission to "Allow"
3. Refresh the page
4. Try again

**Chrome Instructions:**
```
Settings → Privacy and Security → Site Settings 
→ Microphone → Add your ERPNext URL to "Allowed"
```

### Issue: "No speech detected"

**Possible causes:**
- Microphone not working
- Speaking too quietly
- Background noise

**Solutions:**
- Check microphone is connected and working
- Speak louder and clearer
- Reduce background noise
- Try a different microphone

### Issue: "Voice button not visible"

**Cause:** Browser doesn't support Speech Recognition API

**Solutions:**
- Use Google Chrome or Microsoft Edge
- Update browser to latest version
- Enable Web Speech API in Firefox:
  1. Type `about:config` in address bar
  2. Search for `media.webspeech.recognition.enable`
  3. Set to `true`

### Issue: "Recognition stops too early"

**Solution:** Speak more continuously without long pauses

### Issue: "Wrong transcription"

**Tips for better accuracy:**
- Speak clearly and at moderate pace
- Reduce background noise
- Use proper pronunciation
- Say numbers as digits: "one two three" not "123"

## Security & Privacy

### Data Handling

- **Audio NOT sent to our servers**
- Processing done by browser's native API
- Only text transcript used
- Google's Web Speech API may process audio (browser-level)

### Permissions

- Requires microphone permission
- One-time browser permission
- Can be revoked anytime
- No persistent recording

### Privacy Notes

1. **Browser handles all audio processing**
2. **We only receive the text transcript**
3. **No audio files stored**
4. **Standard ERPNext security applies to text queries**

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+V` | Toggle voice input |
| `Esc` | Stop recording (native browser) |
| `Enter` | Send message (after typing) |

## Tips for Best Results

### ✅ DO:
- Speak clearly and at normal pace
- Use a good quality microphone
- Minimize background noise
- Say complete queries
- Use proper grammar

### ❌ DON'T:
- Speak too fast or too slow
- Use in noisy environments
- Expect perfect accuracy (90-95% typical)
- Use with poor quality microphones
- Speak multiple queries at once

## Example Voice Commands

### Effective Commands

```
✅ "Show me pending sales orders"
✅ "Search for customer ABC Corporation"
✅ "What is the stock balance for item laptop?"
✅ "Get details for customer C U S T zero zero one"
✅ "Find purchase orders from supplier XYZ"
```

### Less Effective

```
❌ "Showmependingsalesorders" (too fast, no breaks)
❌ "um... uh... show... uh... orders?" (too many pauses)
❌ "SHOW ME SALES ORDERS!" (shouting, distorted)
```

## Advanced Features

### Multi-language Support

To enable multiple languages, modify the code:

```javascript
// In erpnext_ai_chat.js

// Add language selector
const languages = {
    'en-US': 'English (US)',
    'en-GB': 'English (UK)', 
    'es-ES': 'Spanish',
    'fr-FR': 'French',
    'de-DE': 'German',
    'hi-IN': 'Hindi'
};

// Set based on user preference
erpnext_ai_chat.recognition.lang = userPreferredLanguage;
```

### Continuous Mode

For longer dictation:

```javascript
erpnext_ai_chat.recognition.continuous = true;  // Keep listening
erpnext_ai_chat.recognition.maxAlternatives = 3; // More alternatives
```

## Future Enhancements

Planned features:
- [ ] Language selector in UI
- [ ] Voice output (text-to-speech for responses)
- [ ] Noise cancellation
- [ ] Custom wake words
- [ ] Offline speech recognition
- [ ] Voice commands (e.g., "clear chat", "new session")

## API Reference

### JavaScript API

```javascript
// Start voice input
erpnext_ai_chat.toggleVoiceInput();

// Check if listening
if (erpnext_ai_chat.isListening) {
    // Currently recording
}

// Access recognition object
erpnext_ai_chat.recognition.stop();  // Stop manually
```

### Events

```javascript
// On start
erpnext_ai_chat.recognition.onstart = function() {
    console.log('Started listening');
};

// On result
erpnext_ai_chat.recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    console.log('You said:', transcript);
};

// On error
erpnext_ai_chat.recognition.onerror = function(event) {
    console.error('Error:', event.error);
};
```

## Performance

### Resource Usage
- **CPU:** Low (browser-native)
- **Memory:** ~10-20MB during recording
- **Network:** Minimal (may use Google API)
- **Battery:** Moderate impact on mobile

### Optimization Tips
1. Stop recording when not needed
2. Use headset microphone for better quality
3. Close other tabs using microphone
4. Grant permanent microphone permission

## FAQ

**Q: Does this work offline?**
A: No, requires internet connection for speech recognition.

**Q: What languages are supported?**
A: 50+ languages, default is English (US). Full list at MDN Web Docs.

**Q: Is my voice recorded?**
A: Audio is processed in browser, not stored or sent to our servers.

**Q: Why doesn't it work in Firefox?**
A: Firefox has limited Web Speech API support. Use Chrome/Edge.

**Q: Can I use this on mobile?**
A: Yes! Works on Chrome for Android and Safari for iOS.

**Q: How accurate is it?**
A: Typically 90-95% accurate with clear speech and good microphone.

**Q: Does it understand accents?**
A: Yes, but accuracy varies. US/UK accents work best for English.

---

## Quick Start

1. ✅ **Open AI Chat**
2. ✅ **Click 🎤 button**
3. ✅ **Allow microphone access**
4. ✅ **Speak your query**
5. ✅ **Get AI response!**

**That's it! No typing needed! 🎉**
