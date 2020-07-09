export function deal(msg) {
  $.each(msg.hands, function(player, cards) {
    if (player === sessionStorage.getItem('nickname')) {
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card,
          class: 'player-card',
          src: '/static/img/cards/' + card
        });
        $('#' + player + '-cards').append(cardImage);
      });
      console.log('checking for jokers');
      if ($('#' + player + '-cards').find('img#joker').length !== 0) {
        $('#joker-selector').modal({
          backdrop: 'static',
          keyboard: false
        });
      }
    } else {
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card,
          class: 'opponent-card',
          src: '/static/img/cards/facedown.png'
        });
        $('#' + player + '-cards').append(cardImage);
      });
    }
  });
};

export function showChosenJoker(player, card) {
  if (player === sessionStorage.getItem('nickname')) {
    $('#' + player).find('#joker').remove();
    let cardImage = $('<img/>', {
      id: card,
      class: 'player-card',
      src: '/static/img/cards/' + card
    });
    $('#' + player + '-cards').append(cardImage);
  }
}