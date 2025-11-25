/**
 * Gmail MCP API Service
 * Connects the Email Manager UI to the Gmail MCP HTTP Server
 */

const GMAIL_API_BASE = import.meta.env.VITE_GMAIL_API_URL || 'http://localhost:8001';

/**
 * Fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  try {
    const response = await fetch(`${GMAIL_API_BASE}${endpoint}`, {
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
    console.error(`Gmail API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Gmail API Service
 */
export const gmailApi = {
  /**
   * Health check
   */
  async healthCheck() {
    return fetchApi('/health');
  },

  /**
   * List all configured Gmail accounts
   */
  async listAccounts() {
    return fetchApi('/accounts');
  },

  /**
   * List messages/emails
   * @param {Object} params - Query parameters
   * @param {string} params.accountId - Account ID (primary, arvinda_gillella, firsts_lastn)
   * @param {string} params.query - Gmail search query
   * @param {number} params.maxResults - Max results to return
   * @param {string} params.labelIds - Comma-separated label IDs
   */
  async listMessages({ accountId = 'primary', query, maxResults = 20, labelIds } = {}) {
    const params = new URLSearchParams();
    params.append('account_id', accountId);
    if (query) params.append('query', query);
    if (maxResults) params.append('max_results', maxResults);
    if (labelIds) params.append('label_ids', labelIds);
    
    return fetchApi(`/messages?${params}`);
  },

  /**
   * Get a single message by ID
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async getMessage(messageId, accountId = 'primary') {
    return fetchApi(`/messages/${messageId}?account_id=${accountId}`);
  },

  /**
   * Get all messages in a thread
   * @param {string} threadId - Thread ID
   * @param {string} accountId - Account ID
   */
  async getThread(threadId, accountId = 'primary') {
    return fetchApi(`/threads/${threadId}?account_id=${accountId}`);
  },

  /**
   * Send an email
   * @param {Object} email - Email data
   * @param {string[]} email.to - Recipients
   * @param {string} email.subject - Subject
   * @param {string} email.body - Body content
   * @param {string[]} email.cc - CC recipients
   * @param {string[]} email.bcc - BCC recipients
   * @param {boolean} email.html - Is HTML content
   * @param {string} email.replyToMessageId - Message ID to reply to
   * @param {string} accountId - Account to send from
   */
  async sendEmail(email, accountId = 'primary') {
    return fetchApi(`/messages/send?account_id=${accountId}`, {
      method: 'POST',
      body: JSON.stringify(email),
    });
  },

  /**
   * Create a draft email
   * @param {Object} draft - Draft data
   * @param {string[]} draft.to - Recipients
   * @param {string} draft.subject - Subject
   * @param {string} draft.body - Body content
   * @param {string} accountId - Account ID
   */
  async createDraft(draft, accountId = 'primary') {
    return fetchApi(`/drafts?account_id=${accountId}`, {
      method: 'POST',
      body: JSON.stringify(draft),
    });
  },

  /**
   * Search emails
   * @param {string} query - Gmail search query
   * @param {string} accountId - Account ID
   * @param {number} maxResults - Max results
   */
  async searchEmails(query, accountId = 'primary', maxResults = 20) {
    const params = new URLSearchParams({
      query,
      account_id: accountId,
      max_results: maxResults,
    });
    return fetchApi(`/search?${params}`);
  },

  /**
   * List all labels
   * @param {string} accountId - Account ID
   */
  async listLabels(accountId = 'primary') {
    return fetchApi(`/labels?account_id=${accountId}`);
  },

  /**
   * Modify message labels (mark read/unread, star, etc.)
   * @param {string} messageId - Message ID
   * @param {Object} labels - Labels to add/remove
   * @param {string[]} labels.addLabels - Labels to add
   * @param {string[]} labels.removeLabels - Labels to remove
   * @param {string} accountId - Account ID
   */
  async modifyLabels(messageId, labels, accountId = 'primary') {
    return fetchApi(`/messages/${messageId}/labels?account_id=${accountId}`, {
      method: 'PATCH',
      body: JSON.stringify({
        add_labels: labels.addLabels,
        remove_labels: labels.removeLabels,
      }),
    });
  },

  /**
   * Archive a message (remove from inbox)
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async archiveMessage(messageId, accountId = 'primary') {
    return fetchApi(`/messages/${messageId}/archive?account_id=${accountId}`, {
      method: 'POST',
    });
  },

  /**
   * Move message to trash
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async trashMessage(messageId, accountId = 'primary') {
    return fetchApi(`/messages/${messageId}/trash?account_id=${accountId}`, {
      method: 'POST',
    });
  },

  /**
   * Mark message as read
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async markAsRead(messageId, accountId = 'primary') {
    return this.modifyLabels(messageId, { removeLabels: ['UNREAD'] }, accountId);
  },

  /**
   * Mark message as unread
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async markAsUnread(messageId, accountId = 'primary') {
    return this.modifyLabels(messageId, { addLabels: ['UNREAD'] }, accountId);
  },

  /**
   * Star a message
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async starMessage(messageId, accountId = 'primary') {
    return this.modifyLabels(messageId, { addLabels: ['STARRED'] }, accountId);
  },

  /**
   * Unstar a message
   * @param {string} messageId - Message ID
   * @param {string} accountId - Account ID
   */
  async unstarMessage(messageId, accountId = 'primary') {
    return this.modifyLabels(messageId, { removeLabels: ['STARRED'] }, accountId);
  },
};

/**
 * React Query hooks helpers
 */
export const queryKeys = {
  accounts: ['gmail', 'accounts'],
  messages: (accountId, query) => ['gmail', 'messages', accountId, query],
  message: (messageId, accountId) => ['gmail', 'message', messageId, accountId],
  thread: (threadId, accountId) => ['gmail', 'thread', threadId, accountId],
  labels: (accountId) => ['gmail', 'labels', accountId],
  search: (query, accountId) => ['gmail', 'search', query, accountId],
};

export default gmailApi;

