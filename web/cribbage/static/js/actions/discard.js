export function animateDiscard(discarded) {
  let cardImage = $('<img/>', {
    id: discarded,
    class: 'crib-card',
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
  let discarded = msg.card;
  console.log(msg.nickname + ' just discarded ' + discarded);
  $('#' + discarded).remove();
  animateDiscard(discarded);

  if (msg.done) {
    $('#' + msg.nickname).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
    $('#action-button').prop('disabled', true);
  }

}