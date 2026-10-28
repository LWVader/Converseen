/*
* This file is part of Converseen, an open-source batch image converter
* and resizer.
*
* (C) Francesco Mondello 2009 - 2026
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* Contact e-mail: Francesco Mondello <faster3ck@gmail.com>
*
*/

#include <QUrl>
#include <QDesktopServices>
#include <QTextDocument>
#include "dialoginfo.h"
#include "globals.h"
#include "qpainter.h"

DialogInfo::DialogInfo(QWidget *parent) :
    QDialog(parent){
    setupUi(this);
    // PIXEL SHROOM BRANDING 8.1: original-project credits remain in the About dialog.
    pushFacebook->hide();
    pushDonatePayPal->hide();

    connect(pushClose, SIGNAL(clicked()), this, SLOT(close()));
    connect(pushFacebook, SIGNAL(clicked()), this, SLOT(openFacebookPage()));

    QString appVersion;
    QString magickVersion;
    QString iMVersionStrTr = tr("ImageMagick Version:");
    QString qtVersionStrTr = tr("Qt Version:");

#ifdef Q_OS_WIN32
    appVersion = QString("%1%2")
            .arg(QCoreApplication::applicationVersion())
            .arg(globals::Globals::signature());
#else
    appVersion = QCoreApplication::applicationVersion();
#endif

    QString title = QString("<p><span style=\" font-size:12pt; font-weight:600;\">Pixel Shroom Image Studio %1</span><br />"
                            "<span style=\" font-size:10pt;\">%2</span></p>")
            .arg(appVersion)
            .arg(tr("The batch image converter and resizer."));

    labelTitle->setText(title);

    magickVersion = globals::Globals::magickVersion();
    QString im_versionString = QString("<p><span style=\" font-size:8pt; font-weight:600;\">%1 </span><span style=\" font-size:8pt;\">%2</span></p>")
                                   .arg(iMVersionStrTr)
                                   .arg(magickVersion);

    labelMagickVersion->setText(im_versionString);

    QString qt_versionString = QString("<p><span style=\" font-size:8pt; font-weight:600;\">%1 </span><span style=\" font-size:8pt;\">%2</span></p>")
                                   .arg(qtVersionStrTr)
                                   .arg(QT_VERSION_STR);
    labelQtVersion->setText(qt_versionString);


    // PIXEL SHROOM ABOUT SCREEN 8.2: override legacy About text without changing conversion logic.
    setWindowTitle(QStringLiteral("About Pixel Shroom Image Studio"));
    QString psTitle = labelTitle->text();
    psTitle.replace(QStringLiteral("Converseen"), QStringLiteral("Pixel Shroom Image Studio"));
    labelTitle->setText(psTitle);
    label_3->setText(QStringLiteral(
        "Batch image processing for print and web: resize, compress, enhance, and compare images."));
    groupBox->setTitle(QStringLiteral("Publisher and open-source credits"));
    label->setText(QStringLiteral(
        "<p><b>Customized and maintained by:</b> Pixel Shroom Studio<br>"
        "<b>Official website:</b> <a href='https://www.pixelshroomstudio.com/'>pixelshroomstudio.com</a></p>"
        "<p><b>Open-source foundation:</b> Built from <a href='https://github.com/Faster3ck/Converseen'>Converseen</a> "
        "by Francesco Mondello, with contributions from its open-source community.</p>"));
    label->setOpenExternalLinks(true);
    label->setWordWrap(true);
    label_2->setText(QStringLiteral(
        "Pixel Shroom Studio modifications (c) 2026. "
        "Converseen (c) 2009-2026 Francesco Mondello. "
        "GNU GPL v3 or later. Original project credits and license remain applicable."));
    label_2->setWordWrap(true);

    // Retire upstream-specific donation and social areas; original contributions stay credited.
    label_18->hide();
    pushDonatePayPal->hide();
    label_7->hide();
    pushFacebook->hide();
    line_2->hide();
    line->hide();
    label_6->hide();
    scrollArea->hide();

    // Keep the custom mushroom logo crisp and compact on the About screen.
    const QPixmap psLogo(QStringLiteral(":/Images/res/icon.png"));
    if (!psLogo.isNull()) {
        label_5->setPixmap(psLogo.scaled(88, 88, Qt::KeepAspectRatio, Qt::SmoothTransformation));
        label_5->setFixedSize(88, 88);
    }
    adjustSize();
    resize(680, 400);
}

void DialogInfo::openFacebookPage()
{
    // Retired upstream action in Pixel Shroom Image Studio.
}

void DialogInfo::on_pushDonatePayPal_clicked()
{
    // Retired upstream action in Pixel Shroom Image Studio.
}
