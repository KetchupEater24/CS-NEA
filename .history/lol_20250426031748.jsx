import React, { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, LabelList } from 'recharts';

// Custom colors for pie charts
const COLORS = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#8134AF', '#1E88E5', '#F4511E', '#43A047'];

// Data for all questions based on the survey data
const surveyData = {
  q1: [
    { name: 'Very smooth', value: 15 },
    { name: 'Somewhat smooth', value: 60 },
    { name: 'Laggy at times', value: 20 },
    { name: 'Very slow', value: 5 }
  ],
  q2: [
    { name: 'Very easy', value: 55 },
    { name: 'Easy', value: 30 },
    { name: 'A bit confusing', value: 10 },
    { name: 'Very difficult', value: 5 }
  ],
  q3: [
    { name: 'Very easy', value: 60 },
    { name: 'Easy', value: 25 },
    { name: 'A bit tricky', value: 10 },
    { name: 'Difficult', value: 5 }
  ],
  q4: [
    { name: 'Very useful', value: 50 },
    { name: 'Somewhat useful', value: 30 },
    { name: 'Not useful', value: 10 },
    { name: "I didn't check the analytics", value: 10 }
  ],
  q5: [
    { name: 'Not really', value: 10 },
    { name: "It's okay", value: 35 },
    { name: 'I loved it!', value: 55 }
  ],
  q6: [
    { name: '1 – Not good', value: 2 },
    { name: '2 – Good', value: 8 },
    { name: '3 – Excellent', value: 10 },
    { name: '4 – Absolutely amazing', value: 15 },
    { name: "5 – If the app didn't have this feature, I wouldn't have used it", value: 65 }
  ],
  q7: [
    { name: '1 – Not good', value: 1 },
    { name: '2 – Good', value: 5 },
    { name: '3 – Excellent', value: 9 },
    { name: '4 – Absolutely amazing', value: 20 },
    { name: "5 – If the app didn't have this feature, I wouldn't have used it", value: 65 }
  ],
  q8: [
    { name: '1 – Not easy', value: 5 },
    { name: '2 – Somewhat understandable', value: 10 },
    { name: '3 – Clear', value: 25 },
    { name: '4 – Very clear', value: 60 }
  ],
  q9: [
    { name: "A. No, it didn't meet the expectations I had for it", value: 15 },
    { name: 'B. Yes absolutely, this is something I could put into my day-to-day life', value: 85 }
  ],
  q10: [
    { name: 'A. The spaced repetition feature', value: 10 },
    { name: 'B. The filtering decks/cards by priority and searching features', value: 10 },
    { name: 'C. The user interface (how it looks)', value: 15 },
    { name: 'D. All of the above', value: 65 }
  ],
  complaints: [
    { name: 'Outdated/confusing UI', value: 40 },
    { name: 'Too many ads/paywalls', value: 25 },
    { name: 'Limited analytics', value: 20 },
    { name: 'Inability to use offline', value: 15 }
  ]
};

// Question titles
const questionTitles = {
  q1: "Q1: How was the app performance?",
  q2: "Q2: How easy was it to navigate the app?",
  q3: "Q3: How easy was card creation?",
  q4: "Q4: How useful were the analytics?",
  q5: "Q5: Did you enjoy using the app?",
  q6: "Q6: Rate the filtering feature",
  q7: "Q7: Rate the search feature",
  q8: "Q8: How clear were the instructions?",
  q9: "Q9: Did the app meet your expectations?",
  q10: "Q10: What did you like most about the app?",
  complaints: "User Complaints"
};

// Custom value label formatter to display percentages inside the pie chart
const renderCustomizedLabel = (props) => {
  const { cx, cy, midAngle, innerRadius, outerRadius, percent, index, value } = props;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
  const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor="middle" 
      dominantBaseline="central"
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

// Single pie chart component
const SurveyPieChart = ({ data, title }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <h3 className="text-lg font-medium text-center mb-2">{title}</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="45%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              label={renderCustomizedLabel}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Legend 
              layout="vertical" 
              verticalAlign="middle" 
              align="right"
              wrapperStyle={{ paddingLeft: "20px" }}
              iconSize={10}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Component that displays all pie charts
export default function AllSurveyCharts() {
  const [selectedChart, setSelectedChart] = useState('q1');
  
  const handleChartSelect = (e) => {
    setSelectedChart(e.target.value);
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6">Survey Results</h1>
      
      <div className="mb-6">
        <label htmlFor="chart-select" className="block mb-2">Select chart to display:</label>
        <select 
          id="chart-select" 
          value={selectedChart} 
          onChange={handleChartSelect}
          className="w-full p-2 border rounded"
        >
          <option value="all">All Charts</option>
          {Object.keys(surveyData).map(key => (
            <option key={key} value={key}>{questionTitles[key]}</option>
          ))}
        </select>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {selectedChart === 'all' ? (
          Object.keys(surveyData).map(key => (
            <SurveyPieChart key={key} data={surveyData[key]} title={questionTitles[key]} />
          ))
        ) : (
          <SurveyPieChart data={surveyData[selectedChart]} title={questionTitles[selectedChart]} />
        )}
      </div>
    </div>
  );
}