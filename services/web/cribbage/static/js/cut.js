export function displayFacedownCutCard(card) {
  sessionStorage.setItem('cut', card);
  let deckImage = $('<img/>', {
    id: 'deck',
    class: 'playerCard',
    src: '/static/img/cards/facedown.png'
  });
  $('#deck-area').append(deckImage);
}

export function showCutDeckAction(starting_player) {
  console.log('showing cut deck action to '+ starting_player);
  $('#' + starting_player + ' #action-button').text('Cut deck').prop('disabled', false);
  $("#" + starting_player).find(".panel-heading").css('background', '#1CA1F2');

}

export function displayCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card.id,
    class: 'cutCard',
    src: '/static/img/cards/' + card.hash
  });
  $('#deck-area').append(cutCardImage);
}
