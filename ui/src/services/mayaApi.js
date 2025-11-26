/**
 * Maya AI Email Assistant API Service
 * Connects the UI to Maya's intelligent email management capabilities
 */

const MEDHA_API_BASE = import.meta.env.VITE_MEDHA_API_URL || 'http://localhost:8000';

/**
 * Fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  try {
    const response = await fetch(`${MEDHA_API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Maya API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Maya AI Assistant API
 */
export const mayaApi = {
  /**
   * Chat with Maya
   * @param {string} message - User's message
   * @param {string} sessionId - Optional session ID for context
   * @param {Object} emailContext - Optional email context for replies
   */
  async chat(message, sessionId = null, emailContext = null) {
    return fetchApi('/api/maya/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        email_context: emailContext,
      }),
    });
  },

  /**
   * Triage inbox - get prioritized emails
   * @param {Object} options - Triage options
   * @param {string} options.accountId - Gmail account ID
   * @param {string} options.query - Gmail query
   * @param {number} options.maxResults - Max emails to process
   */
  async triageInbox({ accountId = 'primary', query = 'is:unread', maxResults = 50 } = {}) {
    return fetchApi('/api/maya/triage', {
      method: 'POST',
      body: JSON.stringify({
        account_id: accountId,
        query,
        max_results: maxResults,
      }),
    });
  },

  /**
   * Get daily email digest
   * @param {string} accountId - Account ID
   */
  async getDailyDigest(accountId = 'primary') {
    return fetchApi(`/api/maya/digest?account_id=${accountId}`);
  },

  /**
   * Draft a response to an email
   * @param {Object} email - Email to respond to
   * @param {string} tone - Response tone (professional, friendly, formal, casual)
   * @param {string} maxLength - Response length (short, medium, long)
   * @param {string} additionalContext - Additional context
   */
  async draftResponse(email, tone = 'professional', maxLength = 'medium', additionalContext = null) {
    return fetchApi('/api/maya/draft', {
      method: 'POST',
      body: JSON.stringify({
        email,
        tone,
        max_length: maxLength,
        additional_context: additionalContext,
      }),
    });
  },

  /**
   * Summarize multiple emails
   * @param {Array} emails - List of emails to summarize
   * @param {string} format - Output format (bullet, paragraph, brief)
   */
  async summarizeEmails(emails, format = 'bullet') {
    return fetchApi(`/api/maya/summarize?format=${format}`, {
      method: 'POST',
      body: JSON.stringify(emails),
    });
  },

  // ==================== LEARNING ====================

  /**
   * Learn a new email response pattern
   * @param {Object} pattern - Pattern definition
   */
  async learnPattern(pattern) {
    return fetchApi('/api/maya/learn/pattern', {
      method: 'POST',
      body: JSON.stringify(pattern),
    });
  },

  /**
   * Mark a contact as VIP
   * @param {string} email - Contact email
   * @param {boolean} isVip - VIP status
   * @param {string} reason - Reason for VIP status
   */
  async markVip(email, isVip = true, reason = null) {
    return fetchApi('/api/maya/learn/vip', {
      method: 'POST',
      body: JSON.stringify({
        email,
        is_vip: isVip,
        reason,
      }),
    });
  },

  /**
   * Learn a new preference
   * @param {string} preference - Preference description
   * @param {string} category - Preference category
   */
  async learnPreference(preference, category = 'general') {
    return fetchApi(`/api/maya/learn/preference?preference=${encodeURIComponent(preference)}&category=${category}`, {
      method: 'POST',
    });
  },

  /**
   * Get all learned patterns
   */
  async getPatterns() {
    return fetchApi('/api/maya/patterns');
  },

  // ==================== PIPELINE ====================

  /**
   * Start the email processing pipeline
   * @param {Object} config - Pipeline configuration
   */
  async startPipeline(config = {}) {
    return fetchApi('/api/maya/pipeline/start', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  /**
   * Stop the email pipeline
   */
  async stopPipeline() {
    return fetchApi('/api/maya/pipeline/stop', {
      method: 'POST',
    });
  },

  /**
   * Get pipeline status and stats
   */
  async getPipelineStatus() {
    return fetchApi('/api/maya/pipeline/status');
  },

  /**
   * Get inbox health metrics
   */
  async getInboxHealth() {
    return fetchApi('/api/maya/inbox/health');
  },

  // ==================== MEMORY ====================

  /**
   * Get memory system stats
   */
  async getMemoryStats() {
    return fetchApi('/api/memory/stats');
  },

  /**
   * Get stored preferences
   * @param {string} domain - Optional domain filter
   * @param {string} category - Optional category filter
   */
  async getPreferences(domain = null, category = null) {
    const params = new URLSearchParams();
    if (domain) params.append('domain', domain);
    if (category) params.append('category', category);
    const query = params.toString();
    return fetchApi(`/api/memory/preferences${query ? '?' + query : ''}`);
  },
};

export default mayaApi;

