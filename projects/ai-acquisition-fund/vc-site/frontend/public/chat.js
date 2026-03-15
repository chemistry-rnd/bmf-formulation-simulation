/* ============================================================
   ScaleWithAI VC — Chat Widget
   Vanilla JS, no dependencies (except marked.js from CDN)
   Usage: <script src="chat.js"></script>
          <script>ScaleWithAIChat.init({ apiBase: '...' })</script>
   ============================================================ */

(function () {
  'use strict';

  /* ----------------------------------------------------------
     Configuration
     ---------------------------------------------------------- */
  const DEFAULTS = {
    apiBase: '', // resolved at init
    maxHistoryMessages: 10,
    sessionKey: 'swai_chat_session',
    placeholderText: 'Задайте вопрос...',
  };

  const PRE_BUILT_QUESTIONS = [
    { text: 'Оценить компанию для покупки', icon: 'chart' },
    { text: 'Подобрать компании для приобретения', icon: 'search' },
    { text: 'Составить R&D план', icon: 'beaker' },
    { text: 'Прогноз рынка для моей компании', icon: 'trend' },
    { text: 'Тестовое задание для найма', icon: 'clipboard' },
  ];

  /* SVG Icons (minimal, inline) */
  const ICONS = {
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    headerClose: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>',
    logo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    beaker: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6v7l5 8H4l5-8V3z"/><line x1="9" y1="3" x2="15" y2="3"/></svg>',
    trend: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    clipboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>',
  };

  /* ----------------------------------------------------------
     State
     ---------------------------------------------------------- */
  let config = {};
  let sessionId = '';
  let messages = []; // { role: 'user'|'assistant', content: string }
  let isOpen = false;
  let isStreaming = false;

  /* DOM references */
  let $root, $trigger, $panel, $messagesArea, $welcomeScreen;
  let $textarea, $sendBtn;
  let currentAbortController = null;

  /* ----------------------------------------------------------
     marked.js loader
     ---------------------------------------------------------- */
  let markedReady = false;
  let markedLoadPromise = null;

  function loadMarked() {
    if (markedLoadPromise) return markedLoadPromise;
    if (window.marked) {
      markedReady = true;
      return Promise.resolve();
    }
    markedLoadPromise = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/marked@12/marked.min.js';
      s.onload = function () {
        configureMarked();
        markedReady = true;
        resolve();
      };
      s.onerror = reject;
      document.head.appendChild(s);
    });
    return markedLoadPromise;
  }

  function configureMarked() {
    if (!window.marked) return;
    window.marked.setOptions({
      breaks: true,
      gfm: true,
    });
  }

  function renderMarkdown(text) {
    if (!markedReady || !window.marked) return escapeHtml(text);
    try {
      return window.marked.parse(text);
    } catch (e) {
      return escapeHtml(text);
    }
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /* ----------------------------------------------------------
     Session
     ---------------------------------------------------------- */
  function getSessionId() {
    try {
      var stored = localStorage.getItem(config.sessionKey);
      if (stored) return stored;
    } catch (e) { /* localStorage may be blocked */ }

    var id = 'sess_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
    try { localStorage.setItem(config.sessionKey, id); } catch (e) { /* ignore */ }
    return id;
  }

  /* ----------------------------------------------------------
     DOM Construction
     ---------------------------------------------------------- */
  function createElement(tag, className, attrs) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (attrs) {
      for (var k in attrs) {
        if (k === 'html') el.innerHTML = attrs[k];
        else if (k === 'text') el.textContent = attrs[k];
        else el.setAttribute(k, attrs[k]);
      }
    }
    return el;
  }

  function buildWidget() {
    /* Root container (holds CSS variable scope) */
    $root = createElement('div', 'swai-chat-widget');
    $root.setAttribute('data-swai-chat', '');

    /* -- Trigger button -- */
    $trigger = createElement('button', 'swai-chat-trigger', {
      'aria-label': 'Open chat',
      'type': 'button',
    });
    $trigger.innerHTML =
      '<span class="swai-chat-icon">' + ICONS.chat + '</span>' +
      '<span class="swai-close-icon">' + ICONS.close + '</span>';
    $trigger.addEventListener('click', toggleChat);

    /* -- Panel -- */
    $panel = createElement('div', 'swai-chat-panel');

    /* Header */
    var $header = createElement('div', 'swai-chat-header');
    var $headerLeft = createElement('div', 'swai-chat-header-left');
    var $headerLogo = createElement('div', 'swai-chat-header-logo', { html: ICONS.logo });
    var $headerInfo = createElement('div', 'swai-chat-header-info');
    $headerInfo.innerHTML =
      '<div class="swai-chat-header-title">ScaleWithAI VC</div>' +
      '<div class="swai-chat-header-status">Online</div>';
    $headerLeft.appendChild($headerLogo);
    $headerLeft.appendChild($headerInfo);

    var $headerClose = createElement('button', 'swai-chat-header-close', {
      'aria-label': 'Close chat',
      'type': 'button',
      html: ICONS.headerClose,
    });
    $headerClose.addEventListener('click', closeChat);

    $header.appendChild($headerLeft);
    $header.appendChild($headerClose);

    /* Messages area */
    $messagesArea = createElement('div', 'swai-chat-messages');

    /* Welcome screen */
    $welcomeScreen = buildWelcomeScreen();
    $messagesArea.appendChild($welcomeScreen);

    /* Input area */
    var $inputArea = createElement('div', 'swai-chat-input-area');
    var $inputWrap = createElement('div', 'swai-chat-input-wrap');

    $textarea = createElement('textarea', 'swai-chat-textarea', {
      placeholder: config.placeholderText,
      rows: '1',
    });
    $textarea.addEventListener('input', autoGrow);
    $textarea.addEventListener('keydown', handleKeyDown);

    $sendBtn = createElement('button', 'swai-chat-send', {
      'aria-label': 'Send message',
      'type': 'button',
      html: ICONS.send,
    });
    $sendBtn.addEventListener('click', handleSend);

    $inputWrap.appendChild($textarea);
    $inputWrap.appendChild($sendBtn);
    $inputArea.appendChild($inputWrap);

    /* Footer */
    var $footer = createElement('div', 'swai-chat-footer');
    $footer.innerHTML = '<span>ScaleWithAI VC Assistant</span>';

    /* Assemble */
    $panel.appendChild($header);
    $panel.appendChild($messagesArea);
    $panel.appendChild($inputArea);
    $panel.appendChild($footer);

    $root.appendChild($trigger);
    $root.appendChild($panel);
    document.body.appendChild($root);
  }

  function buildWelcomeScreen() {
    var $w = createElement('div', 'swai-chat-welcome');

    var $icon = createElement('div', 'swai-chat-welcome-icon', { html: ICONS.logo });
    var $title = createElement('div', 'swai-chat-welcome-title', {
      text: 'Чем могу помочь?',
    });
    var $subtitle = createElement('div', 'swai-chat-welcome-subtitle', {
      text: 'AI-ассистент фонда ScaleWithAI VC',
    });

    var $chips = createElement('div', 'swai-chat-chips');
    PRE_BUILT_QUESTIONS.forEach(function (q) {
      var $chip = createElement('button', 'swai-chat-chip', { type: 'button' });
      var $chipIcon = createElement('span', 'swai-chat-chip-icon', { html: ICONS[q.icon] || '' });
      var $chipText = document.createTextNode(q.text);
      $chip.appendChild($chipIcon);
      $chip.appendChild($chipText);
      $chip.addEventListener('click', function () { sendMessage(q.text); });
      $chips.appendChild($chip);
    });

    $w.appendChild($icon);
    $w.appendChild($title);
    $w.appendChild($subtitle);
    $w.appendChild($chips);
    return $w;
  }

  /* ----------------------------------------------------------
     Chat Open / Close
     ---------------------------------------------------------- */
  function toggleChat() {
    if (isOpen) closeChat(); else openChat();
  }

  function openChat() {
    isOpen = true;
    $panel.classList.add('swai-visible');
    $trigger.classList.add('swai-open');
    $trigger.setAttribute('aria-label', 'Close chat');
    setTimeout(function () { $textarea.focus(); }, 350);
  }

  function closeChat() {
    isOpen = false;
    $panel.classList.remove('swai-visible');
    $trigger.classList.remove('swai-open');
    $trigger.setAttribute('aria-label', 'Open chat');
  }

  /* ----------------------------------------------------------
     Input handling
     ---------------------------------------------------------- */
  function autoGrow() {
    $textarea.style.height = 'auto';
    $textarea.style.height = Math.min($textarea.scrollHeight, 120) + 'px';
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSend() {
    var text = $textarea.value.trim();
    if (!text || isStreaming) return;
    sendMessage(text);
  }

  function setInputEnabled(enabled) {
    $textarea.disabled = !enabled;
    $sendBtn.disabled = !enabled;
    if (enabled) {
      $textarea.focus();
    }
  }

  /* ----------------------------------------------------------
     Message rendering
     ---------------------------------------------------------- */
  function hideWelcomeScreen() {
    if ($welcomeScreen && $welcomeScreen.parentNode) {
      $welcomeScreen.remove();
      $welcomeScreen = null;
    }
  }

  function appendMessage(role, content) {
    hideWelcomeScreen();

    var $msg = createElement('div', 'swai-msg swai-msg-' + role);
    var $bubble = createElement('div', 'swai-msg-bubble');

    if (role === 'assistant') {
      $bubble.innerHTML = renderMarkdown(content);
    } else {
      $bubble.textContent = content;
    }

    $msg.appendChild($bubble);
    $messagesArea.appendChild($msg);
    scrollToBottom();
    return $bubble;
  }

  function createStreamingBubble() {
    hideWelcomeScreen();

    var $msg = createElement('div', 'swai-msg swai-msg-bot');
    var $bubble = createElement('div', 'swai-msg-bubble');
    $msg.appendChild($bubble);
    $messagesArea.appendChild($msg);
    scrollToBottom();
    return $bubble;
  }

  function showTypingIndicator() {
    var $typing = createElement('div', 'swai-typing');
    $typing.setAttribute('data-typing', '');
    for (var i = 0; i < 3; i++) {
      $typing.appendChild(createElement('span', 'swai-typing-dot'));
    }
    $messagesArea.appendChild($typing);
    scrollToBottom();
    return $typing;
  }

  function removeTypingIndicator() {
    var $typing = $messagesArea.querySelector('[data-typing]');
    if ($typing) $typing.remove();
  }

  function scrollToBottom() {
    requestAnimationFrame(function () {
      $messagesArea.scrollTop = $messagesArea.scrollHeight;
    });
  }

  /* ----------------------------------------------------------
     API Communication (SSE streaming)
     ---------------------------------------------------------- */
  function sendMessage(text) {
    if (isStreaming) return;

    /* Clear input */
    $textarea.value = '';
    $textarea.style.height = 'auto';

    /* Add user message */
    messages.push({ role: 'user', content: text });
    appendMessage('user', text);

    /* Start streaming */
    isStreaming = true;
    setInputEnabled(false);

    var $typing = showTypingIndicator();

    /* Build message history (last N messages) */
    var historySlice = messages.slice(-config.maxHistoryMessages);

    /* Prepare request */
    var apiUrl = config.apiBase + '/api/chat';
    currentAbortController = new AbortController();

    fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        messages: historySlice,
      }),
      signal: currentAbortController.signal,
    })
      .then(function (response) {
        removeTypingIndicator();

        if (!response.ok) {
          throw new Error('Server error: ' + response.status);
        }

        var contentType = response.headers.get('content-type') || '';

        /* SSE stream */
        if (contentType.includes('text/event-stream')) {
          return handleSSEStream(response);
        }

        /* JSON fallback */
        if (contentType.includes('application/json')) {
          return response.json().then(function (data) {
            var reply = data.message || data.content || data.response || JSON.stringify(data);
            messages.push({ role: 'assistant', content: reply });
            appendMessage('assistant', reply);
          });
        }

        /* Plain text fallback */
        return response.text().then(function (text) {
          messages.push({ role: 'assistant', content: text });
          appendMessage('assistant', text);
        });
      })
      .catch(function (err) {
        removeTypingIndicator();
        if (err.name === 'AbortError') return;
        var errorMsg = 'Произошла ошибка. Попробуйте позже.';
        appendMessage('assistant', errorMsg);
        console.error('[ScaleWithAI Chat]', err);
      })
      .finally(function () {
        isStreaming = false;
        currentAbortController = null;
        setInputEnabled(true);
      });
  }

  function handleSSEStream(response) {
    var reader = response.body.getReader();
    var decoder = new TextDecoder();
    var $bubble = createStreamingBubble();
    var fullText = '';
    var buffer = '';

    /* Throttle markdown re-rendering for performance */
    var renderPending = false;
    function scheduleRender() {
      if (renderPending) return;
      renderPending = true;
      requestAnimationFrame(function () {
        $bubble.innerHTML = renderMarkdown(fullText);
        scrollToBottom();
        renderPending = false;
      });
    }

    function processChunk() {
      return reader.read().then(function (result) {
        if (result.done) {
          /* Final render with complete text */
          $bubble.innerHTML = renderMarkdown(fullText);
          scrollToBottom();
          messages.push({ role: 'assistant', content: fullText });
          return;
        }

        buffer += decoder.decode(result.value, { stream: true });

        /* Parse SSE lines */
        var lines = buffer.split('\n');
        buffer = lines.pop() || ''; // keep incomplete line in buffer

        for (var i = 0; i < lines.length; i++) {
          var line = lines[i].trim();
          if (!line) continue;

          if (line.startsWith('data: ')) {
            var data = line.slice(6);

            if (data === '[DONE]') {
              $bubble.innerHTML = renderMarkdown(fullText);
              scrollToBottom();
              messages.push({ role: 'assistant', content: fullText });
              return;
            }

            try {
              var parsed = JSON.parse(data);
              var token =
                parsed.token ||
                parsed.content ||
                parsed.delta ||
                (parsed.choices && parsed.choices[0] && parsed.choices[0].delta && parsed.choices[0].delta.content) ||
                '';
              if (token) {
                fullText += token;
                scheduleRender();
              }
            } catch (e) {
              /* If not JSON, treat data as raw text token */
              fullText += data;
              scheduleRender();
            }
          }
        }

        return processChunk();
      });
    }

    return processChunk();
  }

  /* ----------------------------------------------------------
     CSS injection
     ---------------------------------------------------------- */
  function injectCSS() {
    /* Check if chat.css is already loaded */
    var links = document.querySelectorAll('link[rel="stylesheet"]');
    for (var i = 0; i < links.length; i++) {
      if (links[i].href && links[i].href.indexOf('chat.css') !== -1) return;
    }

    /* Auto-load chat.css from same directory as chat.js */
    var scripts = document.querySelectorAll('script[src]');
    for (var j = 0; j < scripts.length; j++) {
      var src = scripts[j].getAttribute('src');
      if (src && src.indexOf('chat.js') !== -1) {
        var base = src.replace(/chat\.js(\?.*)?$/, '');
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = base + 'chat.css';
        document.head.appendChild(link);
        return;
      }
    }
  }

  /* ----------------------------------------------------------
     Public API
     ---------------------------------------------------------- */
  function init(opts) {
    opts = opts || {};
    config = {
      apiBase: opts.apiBase || window.location.origin,
      maxHistoryMessages: opts.maxHistoryMessages || DEFAULTS.maxHistoryMessages,
      sessionKey: opts.sessionKey || DEFAULTS.sessionKey,
      placeholderText: opts.placeholderText || DEFAULTS.placeholderText,
    };

    /* Normalize apiBase — strip trailing slash */
    config.apiBase = config.apiBase.replace(/\/+$/, '');

    sessionId = getSessionId();

    /* Load dependencies */
    loadMarked();
    injectCSS();

    /* Build UI */
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', buildWidget);
    } else {
      buildWidget();
    }
  }

  /* Expose */
  window.ScaleWithAIChat = {
    init: init,
    open: function () { if ($trigger) openChat(); },
    close: function () { if ($trigger) closeChat(); },
    toggle: function () { if ($trigger) toggleChat(); },
  };
})();
