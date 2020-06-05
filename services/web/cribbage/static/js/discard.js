function animateDiscard() {
  let cardImage = $('<img/>', {
    class: 'cribCard',
    src: '/static/img/cards/facedown.png'
  });
  var rNum = (Math.random()*10)-5;
  cardImage.css( {
    '-webkit-transform': 'rotate('+rNum+'2deg)',
    '-moz-transform': 'rotate('+rNum+'2deg)'
  } );
  $('#crib-area').append(cardImage);
}

export function discard(msg, dealer) {
  let readyToPeg = false;
  console.log(msg.nickname + ' just discarded');
  console.log(msg.discarded.id + ' is the card id');

  // append to crib area
  animateDiscard();
  if (sessionStorage.getItem('nickname') === msg.nickname) {
    // remove card image
    $('#' + msg.discarded.id).parent().remove();

    // update session
    let cards = JSON.parse(sessionStorage.getItem('cards'));
    cards.splice($.inArray(msg.discarded.hash, cards), 1);
    sessionStorage.setItem('cards', JSON.stringify(cards));

    // check if ready to play
    if (cards.length === 4) {
      readyToPeg = true;
      $('#' + msg.nickname + ' #action-button').text('Cut deck').prop('disabled', true);
    }
  } else {
    $("#" + msg.nickname).find('img').first().remove();
  }
  return readyToPeg;
}