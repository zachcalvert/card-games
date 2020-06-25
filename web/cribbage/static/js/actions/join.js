export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length === 0) {
    let playerName = $('<span/>', {
      class: 'player-nickname',
      html: msg.nickname
    });

    let playerStatus = $('<span/>', {
      class: 'player-status',
    });

    let panelHeading = $('<div/>', {
      class: 'panel-heading',
    });
    panelHeading.append(playerName);
    panelHeading.append(playerStatus);

    let panelBody = $('<div/>', {
      id: msg.nickname + '-cards',
      class: 'panel-body d-flex justify-content-center opponent-cards',
    });
    let playPile = $('<div/>', {
      class: 'play-pile',
    });


    let opponentPanel = $('<div/>', {
      id: msg.nickname,
      class: 'opponent rounded panel panel-default',
    });

    opponentPanel.append(panelHeading);
    opponentPanel.append(panelBody);
    opponentPanel.append(playPile);
    $('.opponents').append(opponentPanel);

    $('.game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}