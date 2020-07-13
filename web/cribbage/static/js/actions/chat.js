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
  if (nickname) {
    message.append('<b>' + nickname + ': </b>');
  }
  message.append(contents);
  $('.game-log').append(message).html();
  updateScroll();
}