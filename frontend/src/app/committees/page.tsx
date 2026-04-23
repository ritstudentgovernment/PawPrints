import Footer from "../components/Footer";
import NavBar from "../components/NavBar";
import BannerCommittees from "../components/BannerCommittees";
import './page.css';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"


export default function Page() {
  return <main className={`main`}>
    <NavBar />
    <BannerCommittees></BannerCommittees>
    <div className={'outer'}>
      {/* <h1>Committees</h1> */}
      <div className="accordion-container">
        <div className="accordion"><Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>Academics and Co-ops</AccordionTrigger>
            <AccordionContent className="committee-content">
              <p>The Academics & Co-ops Committee discusses and proposes
                solutions on issues relating to academic and co-op affairs
                as well as promote ideas for improvement at RIT. Some of
                those projects include:</p>
              <div className={'innerlist'}>
                <ul>
                  <li>Proposing a new grading scale to promote students to
                    challenge themselves through free electives</li>
                  <li>Discussing plans to efficiently using student time during finals
                    week</li>
                  <li>Enforcing reasonable time grade feedback policy
                    Pursuing extending class drop period.</li>
                </ul>
              </div>
              {/* consider wether or not to add meeting times, 
              seems like constant changes would be needed*/}
              {/* <p>This committee meets on  Mondays at 2-3pm in CPC-1740.</p> */}
            </AccordionContent>
          </AccordionItem>
        </Accordion></div>

        <div className="accordion">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1">
              <AccordionTrigger>Accessibility</AccordionTrigger>
              <AccordionContent className="committee-content">
                The Accessibility Committee strives to make the RIT/NTID
                experience more Deaf-Friendly through a variety of initiatives.
                Some of their efforts include:

                <div className={'innerlist'}><ul>
                  <li>Improving acessibility at Dining Services</li>
                  <li>Facilitating understanding and relationships between Monroe
                    County Sheriff's Office and Deaf students</li>
                  <li>ASL education across campus</li>
                </ul></div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>

        <div className="accordion">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1">
              <AccordionTrigger>Facilities, Parking, Transportation and Sustainability</AccordionTrigger>
              <AccordionContent className="committee-content">
                <b>Facilities:</b> Working with Facilities Management Services on issues,
                such as maintenance and cleanliness. Advocating for student needs
                in the form of:

                <div className={'innerlist'}>
                  <ul>
                    <li>Improving cleaning of dorm-side restrooms</li>
                    <li>Bringing back trash cans to all restrooms on dorm-side</li>
                    <li>Addressing the presence of pests, especially mice and
                      cockroaches</li>
                    <li>Better lighting for certain areas of campus</li>
                  </ul>
                </div>

                <b>Parking and Transportation:</b> Working with Parking and
                Transportation Services on issues such as access to parking on
                campus and improved shuttle services. Advocating for student
                needs in the form of:

                <div className={'innerlist'}>
                  <ul>
                    <li>More reliable busses</li>
                    <li>Evaluating the parking situation on campus</li>
                  </ul>
                </div>

                <b>Sustainability:</b> helps look at ways to increase sustainable
                actions on RIT's campus. Some of their current charges include:

                <div className={'innerlist'}>
                  <ul>
                    <li>Establishing special interest housing for environmental
                      sustainability</li>
                    <li>Creating multi-purpose sustainable art installations that
                      promote environmental sustainability while brightening up
                      our campus.</li>
                    <li>Updating our interactive sustainability map to include
                      locations of; recycling bins, bottle return centers,
                      outdoor trash cans, bike racks, water bottle filling
                      stations, the community garden, plant-based dining options, and
                      donation bins, while continuing to increase the number of these
                      on campus.</li>
                  </ul>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion></div>

        <div className="accordion">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1">
              <AccordionTrigger>Housing and Dining</AccordionTrigger>
              <AccordionContent className="committee-content">
                The housing and dining committee contains representatives
                from Housing, Residence Life, Dining, Auxiliary Services,
                Sustainability, and FMS. Some issues currently being
                handled are:

                <div className={'innerlist'}><ul>
                  <li>Managing inflation and rising food costs
                    Overseeing dorm hall renovations</li>
                  <li>Promoting dining initiatives</li>
                  <li>Introducing cultural food events</li>
                  <li>Increasing access for Halal, Kosher, and other dietary
                    restrictions</li>
                </ul></div>
              </AccordionContent>
            </AccordionItem>
          </Accordion></div>


        <div className="accordion"><Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>Student Affairs</AccordionTrigger>
            <AccordionContent className="committee-content">
              Taking a lot of charges relating to improvement of student
              life at RIT, some of the current charges of Student Affairs
              committee are:

              <div className={'innerlist'}><ul>
                <li>Improving Counseling and Psychological services</li>
                <li>Creating a Study Abroad Endowment Scholarship</li>
                <li>Increasing Student Wages</li>
                <li>Promotion of Financial Literacy</li>
              </ul></div>
            </AccordionContent>
          </AccordionItem>
        </Accordion></div>

        <div className="accordion"><Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>Well-Being</AccordionTrigger>
            <AccordionContent className="committee-content">
              The Wellbeing Committee works with offices such as
              Integrated Health Services and RIT FoodShare to promote
              student health and wellness and ensure a thriving and
              inclusive campus community. Examples of work involve:
              <div className={'innerlist'}><ul>
                <li>Bringing visual markers to identify students, faculty,
                  and staff that are equipped with the necessary health
                  resources to guide individuals in the right direction</li>
                <li>Provide resources, events, and support to enhance physical,
                  mental, and emotional well-being</li>
              </ul></div>
            </AccordionContent>
          </AccordionItem>
        </Accordion></div>
      </div>
      

    </div>
    <Footer></Footer>
  </main>

}