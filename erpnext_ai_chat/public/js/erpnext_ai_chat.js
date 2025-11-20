frappe.provide('erpnext_ai_chat');

// Voice recognition setup
erpnext_ai_chat.recognition = null;
erpnext_ai_chat.isListening = false;

// Chart counter for unique IDs
erpnext_ai_chat.chartCounter = 0;

$(document).ready(function() {
    // Add AI Chat button to navbar
    if (frappe.boot.user && frappe.boot.user.name !== 'Guest') {
        addAIChatButton();
        initVoiceRecognition();
    }
});

function addAIChatButton() {
    const chatButton = `
        <li class="nav-item">
            <a class="nav-link" href="#" onclick="erpnext_ai_chat.openChat(); return false;">
                <svg class="icon icon-sm">
                    <use href="#icon-chat"></use>
                </svg>
                <span class="ml-2">AI Assistant</span>
            </a>
        </li>
    `;
    
    setTimeout(() => {
        if ($('.navbar .navbar-nav').length && !$('#ai-chat-button').length) {
            $(chatButton).attr('id', 'ai-chat-button').appendTo('.navbar .navbar-nav');
        }
    }, 1000);
}

function initVoiceRecognition() {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        erpnext_ai_chat.recognition = new SpeechRecognition();
        
        erpnext_ai_chat.recognition.continuous = false;
        erpnext_ai_chat.recognition.interimResults = true;
        erpnext_ai_chat.recognition.lang = 'en-US';
        
        erpnext_ai_chat.recognition.onstart = function() {
            erpnext_ai_chat.isListening = true;
            console.log('Voice recognition started');
        };
        
        erpnext_ai_chat.recognition.onend = function() {
            erpnext_ai_chat.isListening = false;
            console.log('Voice recognition ended');
        };
        
        erpnext_ai_chat.recognition.onerror = function(event) {
            console.error('Voice recognition error:', event.error);
            erpnext_ai_chat.isListening = false;
            
            const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
            const $voiceBtn = $wrapper.find('.ai-chat-voice');
            $voiceBtn.removeClass('listening');
            
            if (event.error === 'no-speech') {
                frappe.show_alert({message: __('No speech detected. Please try again.'), indicator: 'orange'});
            } else if (event.error === 'not-allowed') {
                frappe.show_alert({message: __('Microphone access denied. Please enable it in browser settings.'), indicator: 'red'});
            } else {
                frappe.show_alert({message: __('Voice recognition error: ' + event.error), indicator: 'red'});
            }
        };
        
        erpnext_ai_chat.recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Update input field with transcript
            const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
            const $input = $wrapper.find('.ai-chat-input');
            
            if (finalTranscript) {
                $input.val(finalTranscript.trim());
                // Automatically send the message after brief delay
                setTimeout(() => {
                    if ($input.val().trim()) {
                        erpnext_ai_chat.sendMessage();
                    }
                }, 300);
            } else if (interimTranscript) {
                // Show interim results while speaking
                $input.val(interimTranscript);
            }
        };
    } else {
        console.warn('Speech recognition not supported in this browser');
    }
}

erpnext_ai_chat.openChat = function() {
    if (!erpnext_ai_chat.chatDialog) {
        erpnext_ai_chat.chatDialog = new frappe.ui.Dialog({
            title: __('AI Assistant'),
            size: 'large',
            static: true,
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'chat_container'
                }
            ],
            primary_action_label: __('Close'),
            primary_action: function() {
                erpnext_ai_chat.chatDialog.hide();
            }
        });
        
        erpnext_ai_chat.initChat();
    }
    
    erpnext_ai_chat.chatDialog.show();
};

erpnext_ai_chat.initChat = function() {
    const voiceSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    const voiceButton = voiceSupported ? `
        <button class="btn btn-default ai-chat-voice" title="Voice Input (Click and speak)">
            <span class="voice-status">
                <svg class="voice-wave-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect class="wave-bar bar-1" x="4" y="8" width="2" height="8" rx="1" fill="currentColor"/>
                    <rect class="wave-bar bar-2" x="8" y="5" width="2" height="14" rx="1" fill="currentColor"/>
                    <rect class="wave-bar bar-3" x="12" y="2" width="2" height="20" rx="1" fill="currentColor"/>
                    <rect class="wave-bar bar-4" x="16" y="5" width="2" height="14" rx="1" fill="currentColor"/>
                    <rect class="wave-bar bar-5" x="20" y="8" width="2" height="8" rx="1" fill="currentColor"/>
                </svg>
            </span>
        </button>
    ` : '';
    
    const chatHTML = `
        <div class="ai-chat-wrapper" style="height: 500px; display: flex; flex-direction: column;">
            <div class="ai-chat-messages" style="flex: 1; overflow-y: auto; padding: 15px; background: #f7f7f7; border-radius: 5px; margin-bottom: 15px;">
                <div class="welcome-message" style="text-align: center; color: #888; padding: 20px;">
                    <p><strong>Welcome to ERPNext AI Assistant!</strong></p>
                    <p>Ask me anything about your ERPNext data:</p>
                    <ul style="list-style: none; padding: 0; margin-top: 10px;">
                        <li>💼 "Show me pending sales orders"</li>
                        <li>🔍 "Search for customer XYZ"</li>
                        <li>📦 "What's the stock balance for item ABC?"</li>
                        <li>📊 "Show recent purchase orders"</li>
                    </ul>
                    ${voiceSupported ? '<p style="margin-top: 15px;">🎤 <strong>Try voice input!</strong> Click the microphone and speak your query.</p>' : ''}
                </div>
            </div>
            <div class="ai-chat-input-wrapper" style="display: flex; gap: 10px;">
                <input type="text" class="form-control ai-chat-input" placeholder="Type or use voice..." style="flex: 1;">
                ${voiceButton}
                <button class="btn btn-primary ai-chat-send">
                    <svg class="icon icon-sm">
                        <use href="#icon-arrow-right"></use>
                    </svg>
                    Send
                </button>
            </div>
            <div class="ai-chat-actions" style="margin-top: 10px; display: flex; gap: 10px; align-items: center;">
                <button class="btn btn-sm btn-default ai-chat-new-session">New Chat</button>
                <button class="btn btn-sm btn-default ai-chat-clear">Clear History</button>
                <span class="voice-hint" style="font-size: 0.85em; color: #888; margin-left: auto;">
                    ${voiceSupported ? 'Press Ctrl+Shift+V for voice' : ''}
                </span>
            </div>
        </div>
    `;
    
    erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper.html(chatHTML);
    
    erpnext_ai_chat.currentSessionId = null;
    erpnext_ai_chat.setupEventHandlers();
    erpnext_ai_chat.loadChatHistory();
};

erpnext_ai_chat.setupEventHandlers = function() {
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    
    $wrapper.find('.ai-chat-send').on('click', function() {
        erpnext_ai_chat.sendMessage();
    });
    
    $wrapper.find('.ai-chat-input').on('keypress', function(e) {
        if (e.which === 13 && !e.shiftKey) { // Enter without Shift
            e.preventDefault();
            erpnext_ai_chat.sendMessage();
        }
    });
    
    // Voice input button
    $wrapper.find('.ai-chat-voice').on('click', function() {
        erpnext_ai_chat.toggleVoiceInput();
    });
    
    $wrapper.find('.ai-chat-new-session').on('click', function() {
        erpnext_ai_chat.createNewSession();
    });
    
    $wrapper.find('.ai-chat-clear').on('click', function() {
        erpnext_ai_chat.clearHistory();
    });
    
    // Keyboard shortcut for voice input (Ctrl+Shift+V)
    // Prevent Enter from triggering voice when there's text
    $wrapper.find('.ai-chat-input').on('keydown', function(e) {
        // Only prevent Enter if input is empty and we want voice
        // Otherwise Enter should send message
        if (e.which === 13 && !e.shiftKey) {
            // Let the keypress handler deal with it
            return;
        }
    });
    
    $(document).on('keydown.voice-input', function(e) {
        if (e.ctrlKey && e.shiftKey && e.which === 86) { // Ctrl+Shift+V
            e.preventDefault();
            if (erpnext_ai_chat.chatDialog && erpnext_ai_chat.chatDialog.is_visible) {
                erpnext_ai_chat.toggleVoiceInput();
            }
        }
    });
};

erpnext_ai_chat.toggleVoiceInput = function() {
    if (!erpnext_ai_chat.recognition) {
        frappe.show_alert({message: __('Voice recognition not supported in your browser'), indicator: 'red'});
        return;
    }
    
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    const $voiceBtn = $wrapper.find('.ai-chat-voice');
    const $input = $wrapper.find('.ai-chat-input');
    
    if (erpnext_ai_chat.isListening) {
        // Stop listening
        erpnext_ai_chat.recognition.stop();
        $voiceBtn.removeClass('listening');
    } else {
        // Start listening
        try {
            $input.val(''); // Clear input
            erpnext_ai_chat.recognition.start();
            $voiceBtn.addClass('listening');
            
            frappe.show_alert({
                message: __('Listening... Speak now!'),
                indicator: 'blue'
            });
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            frappe.show_alert({
                message: __('Error starting voice input: ' + error.message),
                indicator: 'red'
            });
        }
    }
};

erpnext_ai_chat.sendMessage = function() {
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    const $input = $wrapper.find('.ai-chat-input');
    const message = $input.val().trim();
    
    if (!message) return;
    
    erpnext_ai_chat.addMessage('user', message);
    $input.val('');
    
    erpnext_ai_chat.addTypingIndicator();
    
    frappe.call({
        method: 'erpnext_ai_chat.api.chat.send_message',
        args: {
            message: message,
            session_id: erpnext_ai_chat.currentSessionId
        },
        callback: function(r) {
            erpnext_ai_chat.removeTypingIndicator();
            
            if (r.message && r.message.success) {
                erpnext_ai_chat.currentSessionId = r.message.session_id;
                const response_text = r.message.response || r.message.message;
                erpnext_ai_chat.addMessage('ai', response_text);
                
                // Render chart if provided
                if (r.message.chart_data) {
                    erpnext_ai_chat.renderChart(r.message.chart_data);
                }
            } else {
                erpnext_ai_chat.addMessage('ai', 'Sorry, I encountered an error processing your request.');
            }
        },
        error: function() {
            erpnext_ai_chat.removeTypingIndicator();
            erpnext_ai_chat.addMessage('ai', 'Sorry, there was a connection error.');
        }
    });
};

erpnext_ai_chat.addMessage = function(type, content) {
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    const $messages = $wrapper.find('.ai-chat-messages');
    
    $messages.find('.welcome-message').remove();
    
    const messageClass = type === 'user' ? 'user-message' : 'ai-message';
    const alignStyle = type === 'user' ? 'margin-left: auto; background: #2490ef; color: white;' : 'margin-right: auto; background: white;';
    
    // Check if content contains HTML table
    const isHtmlContent = content.includes('<table') || content.includes('<div');
    const contentDisplay = isHtmlContent ? content : `<div style="white-space: pre-wrap;">${frappe.utils.escape_html(content)}</div>`;
    
    const messageHTML = `
        <div class="${messageClass}" style="max-width: ${isHtmlContent ? '95%' : '80%'}; padding: 10px 15px; margin-bottom: 10px; border-radius: 10px; ${alignStyle}">
            ${contentDisplay}
            <div style="font-size: 0.75em; opacity: 0.7; margin-top: 5px;">${frappe.datetime.get_time(frappe.datetime.now_datetime())}</div>
        </div>
    `;
    
    $messages.append(messageHTML);
    $messages.scrollTop($messages[0].scrollHeight);
};

erpnext_ai_chat.addTypingIndicator = function() {
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    const $messages = $wrapper.find('.ai-chat-messages');
    
    const typingHTML = `
        <div class="typing-indicator" style="max-width: 80%; padding: 10px 15px; margin-bottom: 10px; border-radius: 10px; background: white;">
            <span>AI is typing</span>
            <span class="dots">
                <span>.</span><span>.</span><span>.</span>
            </span>
        </div>
    `;
    
    $messages.append(typingHTML);
    $messages.scrollTop($messages[0].scrollHeight);
};

erpnext_ai_chat.removeTypingIndicator = function() {
    const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
    $wrapper.find('.typing-indicator').remove();
};

erpnext_ai_chat.loadChatHistory = function() {
    frappe.call({
        method: 'erpnext_ai_chat.api.chat.get_chat_history',
        args: {
            session_id: erpnext_ai_chat.currentSessionId
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
                const $messages = $wrapper.find('.ai-chat-messages');
                $messages.find('.welcome-message').remove();
                
                r.message.forEach(function(msg) {
                    const type = msg.message_type.toLowerCase() === 'human' ? 'user' : 'ai';
                    erpnext_ai_chat.addMessage(type, msg.content);
                });
            }
        }
    });
};

erpnext_ai_chat.createNewSession = function() {
    frappe.call({
        method: 'erpnext_ai_chat.api.chat.create_new_session',
        callback: function(r) {
            if (r.message && r.message.success) {
                erpnext_ai_chat.currentSessionId = r.message.session_id;
                
                const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
                const $messages = $wrapper.find('.ai-chat-messages');
                $messages.empty();
                $messages.html(`
                    <div class="welcome-message" style="text-align: center; color: #888; padding: 20px;">
                        <p><strong>New conversation started!</strong></p>
                    </div>
                `);
                
                frappe.show_alert({message: __('New chat session created'), indicator: 'green'});
            }
        }
    });
};

erpnext_ai_chat.clearHistory = function() {
    if (!erpnext_ai_chat.currentSessionId) {
        frappe.show_alert({message: __('No active session to clear'), indicator: 'orange'});
        return;
    }
    
    frappe.confirm(
        __('Are you sure you want to clear the chat history?'),
        function() {
            frappe.call({
                method: 'erpnext_ai_chat.api.chat.clear_chat_history',
                args: {
                    session_id: erpnext_ai_chat.currentSessionId
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        const $wrapper = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper;
                        const $messages = $wrapper.find('.ai-chat-messages');
                        $messages.empty();
                        $messages.html(`
                            <div class="welcome-message" style="text-align: center; color: #888; padding: 20px;">
                                <p><strong>Chat history cleared!</strong></p>
                            </div>
                        `);
                        
                        frappe.show_alert({message: __('Chat history cleared'), indicator: 'green'});
                    }
                }
            });
        }
    );
};

erpnext_ai_chat.renderChart = function(chartData) {
    if (!chartData) return;
    
    const $messages = erpnext_ai_chat.chatDialog.fields_dict.chat_container.$wrapper.find('.ai-chat-messages');
    
    erpnext_ai_chat.chartCounter++;
    const chartId = 'chart-' + erpnext_ai_chat.chartCounter;
    
    // Add chart container
    $messages.append(`
        <div class="ai-message" style="align-self: flex-start; margin: 10px 0; padding: 15px; background: white; border-radius: 8px; max-width: 90%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div class="chart-container">
                <div id="${chartId}" style="min-height: 300px;"></div>
            </div>
        </div>
    `);
    
    $messages.scrollTop($messages[0].scrollHeight);
    
    // Render chart using Frappe Charts
    setTimeout(() => {
        try {
            new frappe.Chart(`#${chartId}`, {
                title: chartData.title || '',
                data: {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || []
                },
                type: chartData.type || 'bar',
                height: chartData.height || 300,
                colors: chartData.colors || ['#7cd6fd', '#743ee2', '#5e64ff', '#ff5858', '#ffa00a'],
                axisOptions: chartData.axisOptions || {},
                barOptions: chartData.barOptions || {spaceRatio: 0.5},
                lineOptions: chartData.lineOptions || {}
            });
        } catch (e) {
            console.error('Error rendering chart:', e);
            $(`#${chartId}`).html('<p style="color: red;">Error rendering chart: ' + e.message + '</p>');
        }
    }, 100);
};
