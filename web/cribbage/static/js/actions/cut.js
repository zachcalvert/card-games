export function revealCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cut-card',
    src: '/static/img/cards/' + card
  });
  $('#deck-area').append(cutCardImage);
  addPlayPile();
  $('#play-total').text(0);
}

function addPlayPile() {
  let playerPlayArea = $('.player-play-area');
  let playPile = $('<div/>', {
    class: 'play-pile col-3 d-flex justify-content-center',
  });
  playerPlayArea.prepend(playPile);

  let dealtCardsArea = $(playerPlayArea).find('.player-cards');
  $(dealtCardsArea).removeClass('col-12');
  $(dealtCardsArea).addClass('col-9');
}
