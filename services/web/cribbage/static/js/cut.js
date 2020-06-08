export function showCutDeckAction(cutter) {
  let deckImage = $('<img/>', {
    id: 'deck',
    class: 'playerCard',
    src: '/static/img/cards/facedown.png'
  });
  $('#deck-area').append(deckImage);

  console.log('showing cut deck action to '+ cutter);
  $('#' + cutter + ' #action-button').text('Cut deck').prop('disabled', false);
  $("#" + cutter).find(".panel-heading").css('background', '#1CA1F2');
}

export function revealCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cutCard',
    src: '/static/img/cards/' + card
  });
  $('#deck-area').append(cutCardImage);
}
