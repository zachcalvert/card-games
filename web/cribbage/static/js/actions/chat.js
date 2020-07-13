function updateScroll() {
  let gameLog = $(".game-log");
  gameLog.scrollTop(gameLog[0].scrollHeight);
}

export function addMessage(type, nickname, contents) {
  let text = '';
  let message = $('<div/>', {
    class: type + '-message message',
    html: text
  });
  if (type === 'score') {
    message.css({'color': '#2E8B57'});
  }
  message.append(contents);
  $('.game-log').append(message).html();
  updateScroll();
}