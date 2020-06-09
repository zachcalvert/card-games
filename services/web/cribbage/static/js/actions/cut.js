export function revealCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cutCard',
    src: '/static/img/cards/' + card
  });
  $('#deck-area').append(cutCardImage);
}
