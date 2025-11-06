frappe.provide('erpnext_ai_chat');

$(document).ready(function() {
    // Add AI Chat button to navbar
    if (frappe.boot.user && frappe.boot.user.name !== 'Guest') {
        addAIChatButton();
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
                </div>
            </div>
            <div class="ai-chat-input-wrapper" style="display: flex; gap: 10px;">
                <input type="text" class="form-control ai-chat-input" placeholder="Type your message..." style="flex: 1;">
                <button class="btn btn-primary ai-chat-send">
                    <svg class="icon icon-sm">
                        <use href="#icon-arrow-right"></use>
                    </svg>
                    Send
                </button>
            </div>
            <div class="ai-chat-actions" style="margin-top: 10px; display: flex; gap: 10px;">
                <button class="btn btn-sm btn-default ai-chat-new-session">New Chat</button>
                <button class="btn btn-sm btn-default ai-chat-clear">Clear History</button>
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
        if (e.which === 13) {
            erpnext_ai_chat.sendMessage();
        }
    });
    
    $wrapper.find('.ai-chat-new-session').on('click', function() {
        erpnext_ai_chat.createNewSession();
    });
    
    $wrapper.find('.ai-chat-clear').on('click', function() {
        erpnext_ai_chat.clearHistory();
    });
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
                erpnext_ai_chat.addMessage('ai', r.message.message);
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
    
    const messageHTML = `
        <div class="${messageClass}" style="max-width: 80%; padding: 10px 15px; margin-bottom: 10px; border-radius: 10px; ${alignStyle}">
            <div style="white-space: pre-wrap;">${frappe.utils.escape_html(content)}</div>
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
