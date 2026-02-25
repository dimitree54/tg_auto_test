import { escapeHtml } from './escape';

interface MessageEntity {
  type: string;
  offset: number;
  length: number;
  url?: string;
  language?: string;
}

function openTag(entity: MessageEntity): string {
  switch (entity.type) {
    case 'bold': return '<strong>';
    case 'italic': return '<em>';
    case 'underline': return '<u>';
    case 'strikethrough': return '<s>';
    case 'code': return '<code>';
    case 'pre': return entity.language
      ? `<pre><code class="language-${escapeHtml(entity.language)}">`
      : '<pre>';
    case 'url': return '';
    case 'text_url': return `<a href="${escapeHtml(entity.url ?? '')}" target="_blank" rel="noopener">`;
    case 'spoiler': return '<span class="tg-spoiler">';
    default: return '';
  }
}

function closeTag(entity: MessageEntity): string {
  switch (entity.type) {
    case 'bold': return '</strong>';
    case 'italic': return '</em>';
    case 'underline': return '</u>';
    case 'strikethrough': return '</s>';
    case 'code': return '</code>';
    case 'pre': return entity.language ? '</code></pre>' : '</pre>';
    case 'url': return '';
    case 'text_url': return '</a>';
    case 'spoiler': return '</span>';
    default: return '';
  }
}

export function renderEntities(text: string, entities: MessageEntity[]): string {
  if (entities.length === 0) return escapeHtml(text);
  
  const sorted = [...entities].sort((a, b) => 
    a.offset !== b.offset ? a.offset - b.offset : b.length - a.length
  );
  
  let html = '';
  let pos = 0;
  
  for (const entity of sorted) {
    const entityOffset = Math.max(0, Math.min(entity.offset, text.length));
    const entityEnd = Math.max(entityOffset, Math.min(entity.offset + entity.length, text.length));
    
    if (entityOffset > pos) {
      html += escapeHtml(text.slice(pos, entityOffset));
    }
    
    if (entityEnd > entityOffset) {
      const entityText = text.slice(entityOffset, entityEnd);
      
      if (entity.type === 'url') {
        html += `<a href="${escapeHtml(entityText)}" target="_blank" rel="noopener">${escapeHtml(entityText)}</a>`;
      } else {
        html += openTag(entity) + escapeHtml(entityText) + closeTag(entity);
      }
      
      pos = entityEnd;
    }
  }
  
  if (pos < text.length) {
    html += escapeHtml(text.slice(pos));
  }
  
  return html;
}