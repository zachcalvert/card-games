function updateScroll() {
  let gameLog = $(".game-log");
  gameLog.scrollTop(gameLog[0].scrollHeight);
}

export function addMessage(type, nickname, contents) {
  let text = '';
  if ((type !== 'points') && (type !== 'points_scored')) {
    text = '<b style="color: gainsboro">' + nickname + ': </b>';
  }
  let message = $('<div/>', {
    class: type + '-message',
    html: text
  });
  if (type === 'points_scored') {
    message.css({'color': '#2E8B57'});
  }
  message.append(contents);
  $('.game-log').append(message).html();
  updateScroll();
}