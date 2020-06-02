// display cut deck action
export function showCutDeckAction() {
  $('#action-button').html('Cut deck');
};


export function showFacedownCutCard(msg) {
  sessionStorage.setItem('cut', msg.cut_card);
  let cutCardImage = $('<img/>', {
    id: 'facedownCutCard',
    class: 'playerCard',
    src: '/static/img/cards/facedown.png'
  });
  $('#deck').append(cutCardImage);
}


export function showCutCard(msg) {
  let cutCardImage = $('<img/>', {
    id: 'cutCard',
    class: 'playerCard',
    src: '/static/img' + msg.cut_card
  });
  $('#deck').append(cutCardImage);
  $('#facedownCutCard').remove();
}