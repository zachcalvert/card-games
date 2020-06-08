function animateDiscard(discarded) {
  let cardImage = $('<img/>', {
    id: discarded,
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

export function discard(msg) {
  console.log(msg.nickname + ' just discarded ' + msg.discarded);

  animateDiscard();
  if (sessionStorage.getItem('nickname') === msg.nickname) {
    // remove card image
    $('#' + msg.discarded).parent().remove();
  } else {
    $("#" + msg.nickname).find('img').first().remove();
  }
}