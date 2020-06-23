export function revealCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cut-card',
    src: '/static/img/cards/' + card
  });
  $('#deck-area').append(cutCardImage);
  $('#play-total').text(0);
}
