export function discard(msg) {
  let readyToPeg = false;
  console.log(msg.nickname + ' just discarded');
  console.log(msg.discarded + ' is the card id');

  if (sessionStorage.getItem('nickname') === msg.nickname) {
    // remove card image
    $('#' + msg.discarded).parent().remove();
    // update session
    let card_ids = JSON.parse(sessionStorage.getItem('card_ids'));
    card_ids.splice($.inArray(msg.discarded, card_ids), 1);
    sessionStorage.setItem('card_ids', JSON.stringify(card_ids));
    // check if ready to play
    if (card_ids.length === 4) {
      readyToPeg = true;
      $('#' + msg.nickname + ' #action-button').text('Cut deck').prop('disabled', true);
    }
  } else {
    $("#" + msg.nickname).find('img').first().remove();
  }
  return readyToPeg;
}