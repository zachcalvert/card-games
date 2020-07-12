function updateScroll() {
  let gameLog = $(".game-log");
  gameLog.scrollTop(gameLog[0].scrollHeight);
}

export function addMessage(type, nickname, contents) {
  let text = '';
  if (type !== 'points') {
    text = '<b>' + nickname + ': </b>';
  }
  let message = $('<div/>', {
    class: type + '-message',
    html: text
  });
  message.append(contents);
  $('.game-log').append(message).html();
  updateScroll();
}