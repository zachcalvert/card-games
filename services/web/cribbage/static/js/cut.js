export function displayFacedownCutCard(msg) {
  sessionStorage.setItem('cut', msg.cut_card);
  let cutCardImage = $('<img/>', {
    id: 'facedownCutCard',
    class: 'playerCard',
    src: '/static/img/cards/facedown.png'
  });
  $('.cribbage-table').append(cutCardImage);
}

export function showCutDeckAction(starting_player) {
  console.log('showing cut deck action to '+ starting_player);
  $('#' + starting_player + ' #action-button').text('Cut deck').prop('disabled', false);
    $("#" + starting_player).find(".panel-heading").css('background', 'pink');

}

export function displayCutCard(cardImage) {
  $('#facedownCutCard').remove();
  let cutCardImage = $('<img/>', {
    id: 'cutCard',
    class: 'playerCard',
    src: cardImage
  });
  $('.cribbage-table').append(cutCardImage);
}
