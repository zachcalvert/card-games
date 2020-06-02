export function displayFacedownCutCard(msg) {
  sessionStorage.setItem('cut', msg.cut_card);
  let cutCardImage = $('<img/>', {
    id: 'facedownCutCard',
    class: 'playerCard',
    src: '/static/img/cards/facedown.png'
  });
  $('.cribbage-table').append(cutCardImage);
}

export function displayCutCard(msg) {
  let cutCardImage = $('<img/>', {
    id: 'cutCard',
    class: 'playerCard',
    src: '/static/img' + msg.cut_card
  });
  $('.cribbage-table').append(cutCardImage);
  $('#facedownCutCard').remove();
}

export function showCutDeckAction() {
  $('#action-button').html('Cut deck');
}