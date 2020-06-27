export function revealCutCard(card) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cut-card',
    src: '/static/img/cards/' + card
  });
  $('.deck-container').append(cutCardImage);
  addPlayPile();
  $('.count-text').show();
  $('#play-total').show().text(0);
}

function addPlayPile() {
  let playPile = $('<div/>', {
    class: 'play-pile col-3 d-flex justify-content-center',
  });
  $('.player-play-area').prepend(playPile);

  let opponents = $('.opponent');
  $.each(opponents, function(index, opponent) {
      let opponentPlayPile = $('<div/>', {
        class: 'play-pile col-3 d-flex justify-content-center',
      });
      $(opponent).find('.opponent-play-area').prepend(opponentPlayPile);
    });
  $('.player-cards').removeClass('col-12').addClass('col-9');
  $('.opponent-cards').removeClass('col-12').addClass('col-9');
}
