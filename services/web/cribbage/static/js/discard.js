export function discard(msg) {
  console.log(msg.nickname + ' just discarded');
  if (sessionStorage.getItem('nickname') === msg.nickname) {
    // remove card image
    $('#' + msg.discarded).parent().remove();

    // update session
    let card_ids = JSON.parse(sessionStorage.getItem('card_ids'));
    card_ids.splice( $.inArray(msg.discarded, card_ids), 1 );
    sessionStorage.setItem('card_ids', JSON.stringify(card_ids));
      // check if ready to play
      if (card_ids.length === 4) {
        socket.emit('ready_to_peg', {game: gameName, nickname: nickname})
      }
  } else {
    $("#" + msg.nickname).find('img').first().remove();
  }
}