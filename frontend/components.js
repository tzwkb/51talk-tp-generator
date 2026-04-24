const Components = {
  renderLevelSelector(containerId, selectedLevel, onSelectCallback) {
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1'];
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    levels.forEach(lvl => {
      const isSelected = lvl === selectedLevel;
      const div = document.createElement('div');
      div.className = `cursor-pointer rounded-xl border-2 p-4 text-center transition-all ${
        isSelected ? 'border-primary bg-primary-light shadow-sm' : 'border-border bg-card hover:border-primary/50 hover:shadow-sm'
      }`;
      div.innerHTML = `<h3 class="text-xl font-bold ${isSelected ? 'text-primary' : 'text-text-primary'}">${lvl}</h3>`;
      div.onclick = () => {
        onSelectCallback(lvl);
        Components.renderLevelSelector(containerId, lvl, onSelectCallback);
      };
      container.appendChild(div);
    });
  },

  renderFileGrid(containerId, files) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const typeColors = {
      json: 'bg-gray-100 text-gray-600',
      html: 'bg-blue-100 text-blue-600',
      pdf: 'bg-red-100 text-red-600'
    };
    container.innerHTML = files.map(f => {
      const colorClass = typeColors[f.type] || 'bg-gray-100 text-gray-600';
      return `
        <div class="flex items-center justify-between p-3 border border-border rounded-lg bg-surface hover:shadow-sm transition-shadow">
          <div class="flex items-center gap-3 min-w-0">
            <i class="ph ph-file text-2xl text-text-secondary flex-shrink-0"></i>
            <span class="font-mono text-sm truncate" title="${f.name}">${f.name}</span>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span class="text-xs px-2 py-1 rounded font-bold uppercase ${colorClass}">${f.type}</span>
            <a href="${f.path}" target="_blank" class="p-1 hover:bg-black/5 rounded transition-colors text-primary" title="${f.type === 'html' ? 'Preview' : 'Download'}">
              <i class="ph ph-${f.type === 'html' ? 'eye' : 'download-simple'} text-lg"></i>
            </a>
          </div>
        </div>`;
    }).join('');
  },

  async fetchSSE(url, body, callbacks) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error('ReadableStream not supported');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split('\n\n');
        buffer = blocks.pop();
        for (const block of blocks) {
          if (!block.trim()) continue;
          let eventType = 'message';
          let eventData = null;
          for (const line of block.split('\n')) {
            if (line.startsWith('event:')) eventType = line.substring(6).trim();
            if (line.startsWith('data:')) {
              try { eventData = JSON.parse(line.substring(5).trim()); }
              catch { eventData = line.substring(5).trim(); }
            }
          }
          if (eventData && callbacks[eventType]) callbacks[eventType](eventData);
        }
      }
    } catch (err) {
      if (callbacks.error) callbacks.error(err);
    }
  }
};
