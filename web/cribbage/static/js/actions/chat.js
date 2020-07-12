function updateScroll() {
  let gameLog = $(".game-log");
  gameLog.scrollTop(gameLog[0].scrollHeight);
}

export function addMessage(type, nickname, contents) {
  let message = $('<div/>', {
    class: type + '-message',
    html: '<b>' + nickname + ': </b>'
  });
  console.log(message);
  message.append(contents);
  $('.game-log').append(message).html();
  updateScroll();
}