import Footer from "../components/Footer";
import NavBar from "../components/NavBar";
import './page.css';
import idea from '../assets/icon-idea.png';
import share from '../assets/icon-share.png';
import write from '../assets/icon-write.png';
import history from '../assets/history.png';
import BannerAbout from '../components/BannerAbout'


export default function Page() {
    return <main className={`main`}>
        <NavBar />
        <BannerAbout></BannerAbout>
        <div className={'outer'}>
            <div className="history">
                <h1>History</h1>
                <div className="container">
                    <div className="history-text">            
                        <p>Student Government President Ashley Carrington and Vice President Tyler Pierce (2014-2015) sought to improve engagement of RIT Students through a Petition site. The site creates a place for the RIT community to converse on important issues.</p>

                        <br />
                        <p>To remain transparent, this site is an open source project available on <a href="https://github.com/ritstudentgovernment/PawPrints">GitHub</a></p>

                        {/* add another paragraph about new pawprints 2 */}
                    </div>
                    <div className="history-img">
                        <img src={history.src} alt="pawprints logo" />
                    </div> 
                </div>
                               
            </div>
            
            <div className="mid">
                <div className="column1">
                    <div className="column-img">
                        <img src={idea.src} alt="lightbulb" />
                    </div>
                    <div className="column-title">
                        <h1>Have an Idea</h1>
                    </div>
                    <div className="column-text">
                        <p>Search for petitions and if a petition similar to yours already exists, sign that petition.This will help raise support for issue and help you better reach the minimum threshold of 200 signatures (as of 09/28/2014) for receiving an official Student Government response.</p>
                    </div>
                </div>
                <div className="column2">
                    <div className="column-img">
                        <img src={write.src} alt="paper and pen" />  
                    </div>
                    <div className="column-title">
                        <h1>Write your petition</h1>
                    </div>
                    <div className="column-text">
                        <p>Use proper spelling and grammar when writing your petition. This will help other users find the petition more easily. Be sure to review our Moderation Policy before posting.</p>
                    </div>
                </div>
                <div className="column3">
                    <div className="column-img">
                        <img src={share.src} alt="three people with a share button" />
                    </div>
                    <div className="column-title">
                        <h1>Share your petition</h1>
                    </div>
                    <div className="column-text">
                        <p>Use social media to spread awareness of your issue. A petition has one year to reach its threshold. If the threshold is not reached, then the petition is archived and available via the search. Student Government may elect to respond to a petition prior to reaching its threshold.</p>
                    </div>
                </div>
            </div>

            <div className="mod-policy">
                <h1>Moderation Policy</h1>
                <p>Use of this site falls under the <a href="http://www.rit.edu/computerconduct/">RIT Code of Conduct for Computer and Network Use.</a></p>

                <br />

                <p>Student Government reserves the right to edit or remove any petition at any time for violating the Code of Conduct. This includes, but is not limited to, creating an intimidating, hostile or abusive environment for any member of the RIT community, or posting of any obscene, defamatory, threatening, or otherwise harassing petitions.</p>

                <br />

                <p>When using this service, you agree to sign petitions from only one RIT Computer Account. Should you have access to more than one account, you will only sign from your primary student, faculty, or staff account.</p>

                <br />

                <p>Please exercise good judgment when using this service.</p>
            </div>

        </div>
        <Footer></Footer>
    </main>

}